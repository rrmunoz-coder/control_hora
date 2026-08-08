from __future__ import annotations

from flask import abort, session

from ..access import accessible_unit_ids, in_clause
from ..db import connection


PUBLIC_STATES = {"PUBLICADO", "REQUIERE_ACTUALIZACION"}


def _row_to_doc(row):
    if row is None:
        return None
    return {
        "id": int(row[0]),
        "estado": row[1],
        "clasificacion": row[2],
        "id_unidad": int(row[3]),
        "id_propietario": int(row[4]),
        "id_revisor": None if row[5] is None else int(row[5]),
        "activo": row[6],
    }


def load_access_document(document_id: int):
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ID_CONOCIMIENTO, ESTADO, CLASIFICACION,
                       ID_UNIDAD_DUENA, ID_PROPIETARIO, ID_REVISOR, ACTIVO
                FROM GT_CONOCIMIENTO
                WHERE ID_CONOCIMIENTO = :id
                """,
                {"id": int(document_id)},
            )
            return _row_to_doc(cur.fetchone())


def can_view_document(doc: dict) -> bool:
    if not doc or doc["activo"] != "S":
        return False

    role = str(session.get("rol_codigo") or "").upper()
    user_id = int(session.get("id_usuario") or 0)
    if role == "ADMIN":
        return True
    if user_id in {doc["id_propietario"], doc["id_revisor"]}:
        return True

    units = accessible_unit_ids()
    if units is None:
        return True
    if doc["id_unidad"] not in units:
        return False

    if role == "JEFE":
        return True

    return (
        doc["estado"] in PUBLIC_STATES
        and doc["clasificacion"] == "INTERNO"
    )


def can_edit_document(doc: dict) -> bool:
    if not doc or doc["activo"] != "S":
        return False
    role = str(session.get("rol_codigo") or "").upper()
    user_id = int(session.get("id_usuario") or 0)
    if doc["estado"] not in {"BORRADOR", "REQUIERE_ACTUALIZACION"}:
        return False
    if role == "ADMIN" or user_id == doc["id_propietario"]:
        return True
    if role == "JEFE":
        units = accessible_unit_ids()
        return units is None or doc["id_unidad"] in units
    return False


def can_review_document(doc: dict) -> bool:
    if not doc or doc["activo"] != "S":
        return False
    role = str(session.get("rol_codigo") or "").upper()
    user_id = int(session.get("id_usuario") or 0)
    if role == "ADMIN" or user_id == doc["id_revisor"]:
        return True
    if role == "JEFE":
        units = accessible_unit_ids()
        return units is None or doc["id_unidad"] in units
    return False


def assert_document_access(document_id: int, *, edit: bool = False, review: bool = False) -> dict:
    doc = load_access_document(document_id)
    allowed = (
        can_review_document(doc)
        if review
        else can_edit_document(doc)
        if edit
        else can_view_document(doc)
    )
    if not allowed:
        abort(403 if doc else 404)
    return doc


def search_scope(alias: str = "C") -> tuple[str, dict]:
    role = str(session.get("rol_codigo") or "").upper()
    user_id = int(session.get("id_usuario") or 0)
    if role == "ADMIN":
        return "1 = 1", {}

    units = accessible_unit_ids() or set()
    placeholders, binds = in_clause(units, prefix="knowledge_unit")
    binds["knowledge_user"] = user_id

    ownership = (
        f"({alias}.ID_PROPIETARIO = :knowledge_user "
        f"OR {alias}.ID_REVISOR = :knowledge_user)"
    )
    if not units:
        return ownership, binds

    unit_clause = f"{alias}.ID_UNIDAD_DUENA IN ({placeholders})"
    if role == "JEFE":
        return f"({ownership} OR {unit_clause})", binds

    visible = (
        f"({alias}.ESTADO IN ('PUBLICADO','REQUIERE_ACTUALIZACION') "
        f"AND {alias}.CLASIFICACION = 'INTERNO' AND {unit_clause})"
    )
    return f"({ownership} OR {visible})", binds
