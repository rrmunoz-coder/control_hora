from __future__ import annotations

from typing import Any

EDITABLE_STATES = {"PENDIENTE", "OBSERVADO", "RECHAZADO", "REABIERTO"}
LOCKED_STATES = {"ENVIADO", "APROBADO", "CERRADO"}
REVIEW_ACTIONS = {
    "APROBAR": "APROBADO",
    "OBSERVAR": "OBSERVADO",
    "RECHAZAR": "RECHAZADO",
}


def row_dict(cursor, row) -> dict[str, Any] | None:
    if not row:
        return None
    columns = [item[0].lower() for item in cursor.description]
    return dict(zip(columns, row))
