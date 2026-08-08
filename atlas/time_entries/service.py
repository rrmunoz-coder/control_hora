from __future__ import annotations

from datetime import date, timedelta
import re
from typing import Any

import oracledb

from ..db import connection

WEEKDAY_NAMES = (
    "Lunes", "Martes", "Miércoles", "Jueves",
    "Viernes", "Sábado", "Domingo",
)
WEEKDAY_SHORT = ("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom")

ALLOWED_MODALITIES = (
    "PRESENCIAL",
    "REMOTO",
    "VACACIONES",
    "DIA_COMPENSATORIO",
    "PERMISO_FLEXIBLE",
    "DIAS_PROGRESIVOS",
    "DESCANSO_SEMANAL",
)

INTEGER_PATTERN = re.compile(r"^[0-9]+$")


def normalize_week_start(value: str | None) -> date:
    try:
        selected = date.fromisoformat(value) if value else date.today()
    except (TypeError, ValueError) as exc:
        raise ValueError("La semana indicada no es válida.") from exc

    return selected - timedelta(days=selected.weekday())


def build_days(week_start: date) -> list[dict[str, Any]]:
    days: list[dict[str, Any]] = []

    for index in range(7):
        current = week_start + timedelta(days=index)
        days.append(
            {
                "date": current,
                "iso": current.isoformat(),
                "key": current.strftime("%Y%m%d"),
                "name": WEEKDAY_NAMES[index],
                "short": WEEKDAY_SHORT[index],
                "day": current.strftime("%d"),
                "month": current.strftime("%m"),
            }
        )

    return days


def _dict_rows(cursor) -> list[dict[str, Any]]:
    columns = [item[0].lower() for item in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _task_catalog(cursor) -> list[dict[str, Any]]:
    cursor.execute(
        """
        SELECT
            T.ID_TAREA,
            T.CODIGO,
            T.TITULO,
            P.CODIGO AS PROYECTO_CODIGO,
            P.NOMBRE AS PROYECTO_NOMBRE,
            T.CLASIFICACION_COSTO,
            T.PERMITE_IMPUTACION,
            T.ACTIVO,
            P.PERMITE_IMPUTACION AS PROYECTO_PERMITE,
            P.ACTIVO AS PROYECTO_ACTIVO,
            TO_CHAR(P.FECHA_INICIO, 'YYYY-MM-DD') AS PROYECTO_INICIO,
            TO_CHAR(P.FECHA_FIN, 'YYYY-MM-DD') AS PROYECTO_FIN,
            CASE
                WHEN T.ID_PROYECTO IS NOT NULL
                 AND T.CODIGO = 'PRYGEN_' || TO_CHAR(T.ID_PROYECTO)
                THEN 'S'
                ELSE 'N'
            END AS ES_TAREA_PROYECTO
        FROM GT_TAREA T
        LEFT JOIN GT_PROYECTO P
          ON P.ID_PROYECTO = T.ID_PROYECTO
        WHERE T.ACTIVO = 'S'
          AND T.PERMITE_IMPUTACION = 'S'
          AND (
                T.ID_PROYECTO IS NULL
                OR (
                    P.ACTIVO = 'S'
                    AND P.PERMITE_IMPUTACION = 'S'
                )
          )
        ORDER BY
            NVL(P.CODIGO, 'ZZZ'),
            T.CODIGO,
            T.TITULO
        """
    )
    return _dict_rows(cursor)


def get_modalities(cursor) -> list[dict[str, Any]]:
    placeholders = ", ".join(
        f":code_{index}"
        for index, _code in enumerate(ALLOWED_MODALITIES)
    )
    binds = {
        f"code_{index}": code
        for index, code in enumerate(ALLOWED_MODALITIES)
    }

    cursor.execute(
        f"""
        SELECT
            COD_MODALIDAD,
            NOMBRE,
            CONSUME_CAPACIDAD
        FROM GT_MODALIDAD_DIA
        WHERE ACTIVO = 'S'
          AND COD_MODALIDAD IN ({placeholders})
        ORDER BY
            CASE COD_MODALIDAD
                WHEN 'PRESENCIAL' THEN 1
                WHEN 'REMOTO' THEN 2
                WHEN 'VACACIONES' THEN 3
                WHEN 'DIA_COMPENSATORIO' THEN 4
                WHEN 'PERMISO_FLEXIBLE' THEN 5
                WHEN 'DIAS_PROGRESIVOS' THEN 6
                WHEN 'DESCANSO_SEMANAL' THEN 7
                ELSE 99
            END
        """,
        binds,
    )
    return _dict_rows(cursor)


def get_week_sheet(
    user_id: int,
    week_start: date,
) -> dict[str, Any]:
    days = build_days(week_start)
    week_end = days[-1]["date"]

    with connection() as conn:
        with conn.cursor() as cursor:
            tasks = _task_catalog(cursor)
            modalities = get_modalities(cursor)

            cursor.execute(
                """
                SELECT
                    I.ID_TAREA,
                    TO_CHAR(I.FECHA_TRABAJO, 'YYYY-MM-DD') AS FECHA_TRABAJO,
                    I.HORAS,
                    I.COMENTARIO,
                    I.ID_IMPUTACION
                FROM GT_IMPUTACION_HORAS I
                WHERE I.ID_USUARIO = :id_usuario
                  AND I.FECHA_TRABAJO >= :fecha_desde
                  AND I.FECHA_TRABAJO < :fecha_hasta
                ORDER BY
                    I.ID_TAREA,
                    I.FECHA_TRABAJO,
                    I.ID_IMPUTACION
                """,
                {
                    "id_usuario": user_id,
                    "fecha_desde": week_start,
                    "fecha_hasta": week_end + timedelta(days=1),
                },
            )
            raw_entries = _dict_rows(cursor)

            cursor.execute(
                """
                SELECT
                    TO_CHAR(FECHA_DIA, 'YYYY-MM-DD') AS FECHA_DIA,
                    COD_MODALIDAD
                FROM GT_CALENDARIO_PERSONA
                WHERE ID_USUARIO = :id_usuario
                  AND FECHA_DIA >= :fecha_desde
                  AND FECHA_DIA < :fecha_hasta
                """,
                {
                    "id_usuario": user_id,
                    "fecha_desde": week_start,
                    "fecha_hasta": week_end + timedelta(days=1),
                },
            )
            calendar_rows = _dict_rows(cursor)

    task_by_id = {
        int(task["id_tarea"]): task
        for task in tasks
    }

    aggregate: dict[int, dict[str, Any]] = {}

    for entry in raw_entries:
        task_id = int(entry["id_tarea"])
        work_date = entry["fecha_trabajo"]
        hours = entry["horas"]
        numeric_hours = float(hours)

        if not numeric_hours.is_integer():
            raise ValueError(
                "Existen imputaciones históricas con decimales en esta semana. "
                "Regularízalas antes de usar la planilla semanal."
            )

        task_data = aggregate.setdefault(
            task_id,
            {
                "hours": {},
                "comment": "",
            },
        )
        task_data["hours"][work_date] = (
            int(task_data["hours"].get(work_date, 0))
            + int(numeric_hours)
        )

        if entry["comentario"]:
            task_data["comment"] = entry["comentario"]

    selected_tasks: list[dict[str, Any]] = []

    for task_id in sorted(
        aggregate,
        key=lambda item: (
            task_by_id.get(item, {}).get("proyecto_codigo") or "ZZZ",
            task_by_id.get(item, {}).get("codigo") or "",
        ),
    ):
        task = task_by_id.get(task_id)
        if not task:
            continue

        selected_tasks.append(
            {
                **task,
                "hours": aggregate[task_id]["hours"],
                "comment": aggregate[task_id]["comment"],
            }
        )

    day_modalities = {
        row["fecha_dia"]: row["cod_modalidad"]
        for row in calendar_rows
    }

    for index, day in enumerate(days):
        default_modality = (
            "PRESENCIAL"
            if index < 5
            else "DESCANSO_SEMANAL"
        )
        day_modalities.setdefault(
            day["iso"],
            default_modality,
        )

    return {
        "week_start": week_start,
        "week_end": week_end,
        "days": days,
        "tasks": tasks,
        "selected_tasks": selected_tasks,
        "modalities": modalities,
        "day_modalities": day_modalities,
    }


def _strict_nonnegative_integer(
    raw_value: str | None,
    field_name: str,
) -> int:
    value = (raw_value or "").strip()

    if not value:
        return 0

    if not INTEGER_PATTERN.fullmatch(value):
        raise ValueError(
            f"{field_name} debe ser un número entero sin decimales."
        )

    return int(value)


def _clean_comment(raw_value: str | None) -> str | None:
    value = (raw_value or "").strip()

    if not value:
        return None

    if len(value) > 2000:
        raise ValueError(
            "El comentario de una tarea no puede superar 2.000 caracteres."
        )

    return value


def _parse_selected_task_ids(form) -> list[int]:
    selected: list[int] = []

    for raw_value in form.getlist("selected_task_ids"):
        try:
            task_id = int(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Se recibió una tarea no válida.") from exc

        if task_id <= 0:
            raise ValueError("Se recibió una tarea no válida.")

        if task_id not in selected:
            selected.append(task_id)

    return selected


def _validate_modalities(
    form,
    days: list[dict[str, Any]],
    valid_modalities: set[str],
) -> dict[str, str]:
    result: dict[str, str] = {}

    for day in days:
        code = (
            form.get(f"modalidad_{day['key']}", "")
            .strip()
            .upper()
        )

        if code not in valid_modalities:
            raise ValueError(
                f"Debes seleccionar un tipo de día válido para {day['name']}."
            )

        result[day["iso"]] = code

    return result


def save_week(
    user_id: int,
    week_start: date,
    form,
) -> dict[str, Any]:
    days = build_days(week_start)
    week_end = days[-1]["date"]
    selected_task_ids = _parse_selected_task_ids(form)

    with connection() as conn:
        with conn.cursor() as cursor:
            tasks = _task_catalog(cursor)
            modalities = get_modalities(cursor)

    valid_task_ids = {
        int(task["id_tarea"])
        for task in tasks
    }
    valid_modalities = {
        str(item["cod_modalidad"])
        for item in modalities
    }

    invalid_tasks = [
        task_id
        for task_id in selected_task_ids
        if task_id not in valid_task_ids
    ]
    if invalid_tasks:
        raise ValueError(
            "Una de las tareas seleccionadas ya no está activa."
        )

    selected_modalities = _validate_modalities(
        form,
        days,
        valid_modalities,
    )

    comments = {
        task_id: _clean_comment(form.get(f"comment_{task_id}"))
        for task_id in selected_task_ids
    }

    posted_hours: dict[tuple[int, str], int] = {}

    for task_id in selected_task_ids:
        for day in days:
            posted_hours[(task_id, day["iso"])] = (
                _strict_nonnegative_integer(
                    form.get(f"hours_{task_id}_{day['key']}"),
                    f"Horas de {day['name']}",
                )
            )

    saved_cells = 0
    deleted_cells = 0
    weekly_total = 0

    with connection(commit=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT ID_TAREA
                FROM GT_IMPUTACION_HORAS
                WHERE ID_USUARIO = :id_usuario
                  AND FECHA_TRABAJO >= :fecha_desde
                  AND FECHA_TRABAJO < :fecha_hasta
                """,
                {
                    "id_usuario": user_id,
                    "fecha_desde": week_start,
                    "fecha_hasta": week_end + timedelta(days=1),
                },
            )
            existing_task_ids = {
                int(row[0])
                for row in cursor.fetchall()
            }

            task_ids_to_process = (
                existing_task_ids | set(selected_task_ids)
            )

            for day in days:
                cursor.execute(
                    """
                    MERGE INTO GT_CALENDARIO_PERSONA C
                    USING (
                        SELECT
                            :id_usuario AS ID_USUARIO,
                            :fecha_dia AS FECHA_DIA,
                            :cod_modalidad AS COD_MODALIDAD
                        FROM DUAL
                    ) X
                    ON (
                        C.ID_USUARIO = X.ID_USUARIO
                        AND C.FECHA_DIA = X.FECHA_DIA
                    )
                    WHEN MATCHED THEN
                        UPDATE SET
                            C.COD_MODALIDAD = X.COD_MODALIDAD
                    WHEN NOT MATCHED THEN
                        INSERT (
                            ID_USUARIO,
                            FECHA_DIA,
                            COD_MODALIDAD
                        )
                        VALUES (
                            X.ID_USUARIO,
                            X.FECHA_DIA,
                            X.COD_MODALIDAD
                        )
                    """,
                    {
                        "id_usuario": user_id,
                        "fecha_dia": day["date"],
                        "cod_modalidad": selected_modalities[day["iso"]],
                    },
                )

            for task_id in sorted(task_ids_to_process):
                if task_id not in valid_task_ids:
                    raise ValueError(
                        "Existe una imputación asociada a una tarea "
                        "que ya no está activa. Debe ser regularizada."
                    )

                comment = comments.get(task_id)

                for day in days:
                    hours = posted_hours.get(
                        (task_id, day["iso"]),
                        0,
                    )
                    out_id = cursor.var(oracledb.NUMBER)

                    cursor.callproc(
                        "PKG_GT_IMPUTACION.GUARDAR_DIA",
                        [
                            user_id,
                            task_id,
                            day["date"],
                            hours,
                            out_id,
                            comment,
                            user_id,
                            "MANUAL",
                        ],
                    )

                    if hours > 0:
                        weekly_total += hours
                        saved_cells += 1
                    else:
                        deleted_cells += 1

    return {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "selected_tasks": len(selected_task_ids),
        "saved_cells": saved_cells,
        "cleared_cells": deleted_cells,
        "weekly_total": weekly_total,
        "modalities": selected_modalities,
    }
