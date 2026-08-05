from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..access import accessible_unit_ids, assert_unit_access, in_clause
from ..audit import record_event
from ..db import connection
from ..errors import flash_exception
from ..security import login_required, roles_required
from ..utils import parse_date, parse_decimal

bp = Blueprint("tasks", __name__, url_prefix="/tareas")


def _task_scope():
    units = accessible_unit_ids()
    if units is None:
        return "1 = 1", {}
    placeholders, binds = in_clause(units, prefix="task_unit")
    binds["current_user"] = int(session["id_usuario"])
    return (
        f"(T.ID_UNIDAD_DUENA IN ({placeholders}) "
        "OR P.ID_RESPONSABLE = :current_user "
        "OR EXISTS (SELECT 1 FROM GT_TAREA_ASIGNACION TA "
        "WHERE TA.ID_TAREA = T.ID_TAREA AND TA.ID_USUARIO = :current_user "
        "AND TA.ACTIVO = 'S'))",
        binds,
    )


def _catalogs():
    units_scope = accessible_unit_ids()
    with connection() as conn:
        with conn.cursor() as cur:
            if units_scope is None:
                unit_condition = "1 = 1"
                binds = {}
            else:
                placeholders, binds = in_clause(units_scope, prefix="catalog_unit")
                unit_condition = f"ID_UNIDAD_DUENA IN ({placeholders})"
            cur.execute(
                f"""
                SELECT ID_PROYECTO, CODIGO, NOMBRE, CLASIFICACION_COSTO, ID_UNIDAD_DUENA
                FROM GT_PROYECTO
                WHERE ACTIVO = 'S'
                  AND {unit_condition}
                ORDER BY CODIGO
                """,
                binds,
            )
            projects = cur.fetchall()

            if units_scope is None:
                cur.execute(
                    """
                    SELECT ID_UNIDAD, CODIGO, NOMBRE, TIPO_UNIDAD
                    FROM GT_ORG_UNIDAD WHERE ACTIVO = 'S'
                    ORDER BY TIPO_UNIDAD, NOMBRE
                    """
                )
                units = cur.fetchall()
                cur.execute(
                    """
                    SELECT ID_USUARIO, NOMBRE FROM GT_USUARIO
                    WHERE ACTIVO = 'S' ORDER BY NOMBRE
                    """
                )
                users = cur.fetchall()
            else:
                placeholders, unit_binds = in_clause(units_scope, prefix="user_unit")
                cur.execute(
                    f"""
                    SELECT ID_UNIDAD, CODIGO, NOMBRE, TIPO_UNIDAD
                    FROM GT_ORG_UNIDAD
                    WHERE ACTIVO = 'S' AND ID_UNIDAD IN ({placeholders})
                    ORDER BY TIPO_UNIDAD, NOMBRE
                    """,
                    unit_binds,
                )
                units = cur.fetchall()
                cur.execute(
                    f"""
                    SELECT DISTINCT U.ID_USUARIO, U.NOMBRE
                    FROM GT_USUARIO U
                    JOIN GT_USUARIO_UNIDAD UU ON UU.ID_USUARIO = U.ID_USUARIO
                    WHERE U.ACTIVO = 'S' AND UU.ACTIVO = 'S'
                      AND UU.ID_UNIDAD IN ({placeholders})
                    ORDER BY U.NOMBRE
                    """,
                    unit_binds,
                )
                users = cur.fetchall()
    return projects, units, users


@bp.route("")
@login_required
def list_tasks():
    condition, binds = _task_scope()
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    T.ID_TAREA, T.CODIGO, T.TITULO, P.CODIGO AS PROYECTO,
                    U.NOMBRE AS UNIDAD, T.CLASIFICACION_COSTO, T.ESTADO,
                    T.PRIORIDAD, TO_CHAR(T.FECHA_COMPROMISO, 'YYYY-MM-DD'),
                    T.PERMITE_IMPUTACION, T.ACTIVO
                FROM GT_TAREA T
                LEFT JOIN GT_PROYECTO P ON P.ID_PROYECTO = T.ID_PROYECTO
                JOIN GT_ORG_UNIDAD U ON U.ID_UNIDAD = T.ID_UNIDAD_DUENA
                WHERE NOT (
                    T.ID_PROYECTO IS NOT NULL
                    AND T.CODIGO = 'PRYGEN_' || TO_CHAR(T.ID_PROYECTO)
                )
                  AND {condition}
                ORDER BY
                    CASE T.PRIORIDAD WHEN 'CRITICA' THEN 1 WHEN 'ALTA' THEN 2 WHEN 'MEDIA' THEN 3 ELSE 4 END,
                    T.FECHA_COMPROMISO NULLS LAST, T.CODIGO
                """,
                binds,
            )
            rows = cur.fetchall()
    return render_template("tasks/list.html", tasks=rows)


@bp.route("/nueva", methods=["GET", "POST"])
@roles_required("ADMIN", "JEFE")
def create_task():
    projects, units, users = _catalogs()

    if request.method == "POST":
        try:
            unit_id = int(request.form["id_unidad"])
            assert_unit_access(unit_id, manage=True)
            project_id = int(request.form["id_proyecto"]) if request.form.get("id_proyecto") else None
            project_map = {int(row[0]): int(row[4]) for row in projects}
            if project_id and project_id not in project_map:
                from flask import abort
                abort(403)
            if project_id and project_map[project_id] != unit_id:
                raise ValueError("La tarea y el proyecto deben pertenecer a la misma unidad.")

            start_date = parse_date(request.form["fecha_inicio"], "Fecha de inicio") if request.form.get("fecha_inicio") else None
            due_date = parse_date(request.form["fecha_compromiso"], "Fecha de compromiso") if request.form.get("fecha_compromiso") else None
            if start_date and due_date and due_date < start_date:
                raise ValueError("La fecha de compromiso no puede ser anterior al inicio.")

            estimated = request.form.get("horas_estimadas", "").strip()
            estimated_value = None if not estimated else parse_decimal(estimated, "Horas estimadas")
            if estimated_value is not None and estimated_value < 0:
                raise ValueError("Las horas estimadas no pueden ser negativas.")

            responsible = int(request.form["id_responsable"]) if request.form.get("id_responsable") else None
            if responsible and responsible not in {int(row[0]) for row in users}:
                from flask import abort
                abort(403)

            with connection(commit=True) as conn:
                with conn.cursor() as cur:
                    out_id = cur.var(int)
                    cur.execute(
                        """
                        INSERT INTO GT_TAREA (
                            CODIGO, TITULO, DESCRIPCION, ID_PROYECTO,
                            ID_UNIDAD_DUENA, CLASIFICACION_COSTO, ESTADO,
                            PRIORIDAD, FECHA_INICIO, FECHA_COMPROMISO,
                            HORAS_ESTIMADAS, PERMITE_IMPUTACION, ACTIVO
                        ) VALUES (
                            :codigo, :titulo, :descripcion, :id_proyecto,
                            :id_unidad, :clasificacion, :estado,
                            :prioridad, :fecha_inicio, :fecha_compromiso,
                            :horas_estimadas, :permite_imputacion, 'S'
                        ) RETURNING ID_TAREA INTO :id_tarea
                        """,
                        {
                            "codigo": request.form.get("codigo", "").strip().upper(),
                            "titulo": request.form.get("titulo", "").strip(),
                            "descripcion": request.form.get("descripcion") or None,
                            "id_proyecto": project_id,
                            "id_unidad": unit_id,
                            "clasificacion": request.form["clasificacion_costo"],
                            "estado": request.form["estado"],
                            "prioridad": request.form["prioridad"],
                            "fecha_inicio": start_date,
                            "fecha_compromiso": due_date,
                            "horas_estimadas": estimated_value,
                            "permite_imputacion": request.form.get("permite_imputacion", "N"),
                            "id_tarea": out_id,
                        },
                    )
                    task_id = int(out_id.getvalue()[0])
                    if responsible:
                        cur.execute(
                            """
                            INSERT INTO GT_TAREA_ASIGNACION (
                                ID_TAREA, ID_USUARIO, TIPO_ASIGNACION
                            ) VALUES (:id_tarea, :id_usuario, 'RESPONSABLE')
                            """,
                            {"id_tarea": task_id, "id_usuario": responsible},
                        )

            record_event("TAREAS", "GT_TAREA", "INSERT", task_id)
            flash("Tarea creada correctamente.", "success")
            return redirect(url_for("tasks.list_tasks"))
        except Exception as exc:
            flash_exception(exc, context="Creación de tarea")

    return render_template("tasks/form.html", projects=projects, units=units, users=users)
