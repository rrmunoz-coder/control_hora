from __future__ import annotations

from datetime import date
from typing import Any

from flask import abort

from ..access import accessible_unit_ids, in_clause
from ..approvals.service import assert_week_editable, get_period
from ..db import connection
from . import service as legacy


def _allowed_task_ids(user_id: int, role_code: str | None) -> set[int]:
    units = accessible_unit_ids(user_id, role_code)
    binds: dict[str, Any] = {"current_user": user_id}
    if units is None:
        scope = "1 = 1"
    else:
        placeholders, unit_binds = in_clause(units, prefix="entry_unit")
        binds.update(unit_binds)
        scope = (
            f"(T.ID_UNIDAD_DUENA IN ({placeholders}) "
            "OR P.ID_RESPONSABLE = :current_user "
            "OR EXISTS (SELECT 1 FROM GT_TAREA_ASIGNACION TA "
            "WHERE TA.ID_TAREA = T.ID_TAREA "
            "AND TA.ID_USUARIO = :current_user AND TA.ACTIVO = 'S'))"
        )
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT T.ID_TAREA
                FROM GT_TAREA T
                LEFT JOIN GT_PROYECTO P ON P.ID_PROYECTO = T.ID_PROYECTO
                WHERE T.ACTIVO = 'S'
                  AND T.PERMITE_IMPUTACION = 'S'
                  AND (T.ID_PROYECTO IS NULL OR (P.ACTIVO = 'S' AND P.PERMITE_IMPUTACION = 'S'))
                  AND {scope}
                """,
                binds,
            )
            return {int(row[0]) for row in cur.fetchall()}


def get_week_sheet(user_id: int, week_start: date, role_code: str | None = None) -> dict[str, Any]:
    sheet = legacy.get_week_sheet(user_id, week_start)
    allowed = _allowed_task_ids(user_id, role_code)
    sheet["tasks"] = [item for item in sheet["tasks"] if int(item["id_tarea"]) in allowed]
    sheet["selected_tasks"] = [
        item for item in sheet["selected_tasks"] if int(item["id_tarea"]) in allowed
    ]
    period = get_period(user_id, week_start)
    sheet["period"] = period
    sheet["week_editable"] = bool(period["editable"])
    return sheet


def save_week(user_id: int, week_start: date, form, role_code: str | None = None) -> dict[str, Any]:
    assert_week_editable(user_id, week_start)
    allowed = _allowed_task_ids(user_id, role_code)
    selected: set[int] = set()
    for raw in form.getlist("selected_task_ids"):
        try:
            selected.add(int(raw))
        except (TypeError, ValueError) as exc:
            raise ValueError("Se recibió una tarea no válida.") from exc
    if not selected.issubset(allowed):
        abort(403)
    return legacy.save_week(user_id, week_start, form)


normalize_week_start = legacy.normalize_week_start
