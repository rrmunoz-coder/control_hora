from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flask import session

from ..access import accessible_unit_ids, assert_unit_access, in_clause
from ..audit import write_event
from ..db import connection
from .access import (
    assert_document_access,
    can_edit_document,
    can_review_document,
    search_scope,
)


DOCUMENT_TYPES = (
    "PROCEDIMIENTO",
    "INSTRUCTIVO",
    "MANUAL",
    "CHECKLIST_CONTROL",
    "REGLA_NEGOCIO",
    "DECISION_OPERACIONAL",
    "INCIDENTE_SOLUCION",
    "SCRIPT_HERRAMIENTA",
    "DOCUMENTO_PROYECTO",
    "PLANTILLA",
    "EVIDENCIA_REFERENCIA",
)
CLASSIFICATIONS = ("INTERNO", "RESTRINGIDO", "CONFIDENCIAL")
STATES = (
    "BORRADOR",
    "EN_REVISION",
    "PUBLICADO",
    "REQUIERE_ACTUALIZACION",
    "OBSOLETO",
)
RELATION_TYPES = ("UNIDAD", "PROYECTO", "SERVICIO", "PROCESO", "ACTIVIDAD", "ACCION", "TAREA")

TRANSITIONS = {
    "BORRADOR": {"EN_REVISION"},
    "EN_REVISION": {"BORRADOR", "PUBLICADO"},
    "PUBLICADO": {"REQUIERE_ACTUALIZACION", "OBSOLETO"},
    "REQUIERE_ACTUALIZACION": {"BORRADOR", "OBSOLETO"},
    "OBSOLETO": set(),
}


@dataclass(frozen=True)
class KnowledgePayload:
    tipo: str
    titulo: str
    resumen: str | None
    contenido: str | None
    etiquetas: str | None
    id_unidad: int
    id_revisor: int | None
    clasificacion: str
    fecha_vigencia: Any = None
    fecha_prox_revision: Any = None
    motivo: str | None = None


def _text(value: Any, limit: int, *, required: bool = False) -> str | None:
    result = str(value or "").strip()
    if required and not result:
        raise ValueError("Falta un campo obligatorio.")
    if len(result) > limit:
        raise ValueError(f"El texto supera el máximo permitido de {limit} caracteres.")
    return result or None


def normalize_payload(payload: KnowledgePayload) -> KnowledgePayload:
    tipo = str(payload.tipo or "").strip().upper()
    clasificacion = str(payload.clasificacion or "").strip().upper()
    if tipo not in DOCUMENT_TYPES:
        raise ValueError("Tipo documental no válido.")
    if clasificacion not in CLASSIFICATIONS:
        raise ValueError("Clasificación documental no válida.")
    assert_unit_access(int(payload.id_unidad), manage=False)
    return KnowledgePayload(
        tipo=tipo,
        titulo=_text(payload.titulo, 250, required=True) or "",
        resumen=_text(payload.resumen, 1000),
        contenido=_text(payload.contenido, 200000),
        etiquetas=_text(payload.etiquetas, 1000),
        id_unidad=int(payload.id_unidad),
        id_revisor=None if payload.id_revisor is None else int(payload.id_revisor),
        clasificacion=clasificacion,
        fecha_vigencia=payload.fecha_vigencia,
        fecha_prox_revision=payload.fecha_prox_revision,
        motivo=_text(payload.motivo, 1000),
    )


def _lob(value):
    return value.read() if hasattr(value, "read") else value


def _document_dict(row) -> dict | None:
    if row is None:
        return None
    return {
        "id": int(row[0]),
        "tipo": row[1],
        "titulo": row[2],
        "resumen": row[3],
        "contenido": _lob(row[4]),
        "etiquetas": row[5],
        "estado": row[6],
        "id_unidad": int(row[7]),
        "unidad": row[8],
        "id_propietario": int(row[9]),
        "propietario": row[10],
        "id_revisor": None if row[11] is None else int(row[11]),
        "revisor": row[12],
        "clasificacion": row[13],
        "version": int(row[14]),
        "fecha_vigencia": row[15],
        "fecha_prox_revision": row[16],
        "motivo": row[17],
        "fecha_creacion": row[18],
        "fecha_modificacion": row[19],
        "activo": row[20],
    }


def search_documents(*, query: str = "", tipo: str = "", estado: str = "") -> list[dict]:
    scope, binds = search_scope("C")
    conditions = ["C.ACTIVO = 'S'", scope]
    query = str(query or "").strip()
    tipo = str(tipo or "").strip().upper()
    estado = str(estado or "").strip().upper()

    if query:
        conditions.append(
            "(UPPER(C.TITULO) LIKE :q OR UPPER(NVL(C.RESUMEN,' ')) LIKE :q "
            "OR UPPER(NVL(C.ETIQUETAS,' ')) LIKE :q)"
        )
        binds["q"] = f"%{query.upper()}%"
    if tipo:
        if tipo not in DOCUMENT_TYPES:
            raise ValueError("Tipo documental no válido.")
        conditions.append("C.TIPO = :tipo")
        binds["tipo"] = tipo
    if estado:
        if estado not in STATES:
            raise ValueError("Estado documental no válido.")
        conditions.append("C.ESTADO = :estado")
        binds["estado"] = estado

    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT C.ID_CONOCIMIENTO, C.TIPO, C.TITULO, C.RESUMEN,
                       C.ESTADO, C.CLASIFICACION, C.VERSION_ACTUAL,
                       U.NOMBRE AS UNIDAD, P.NOMBRE AS PROPIETARIO,
                       R.NOMBRE AS REVISOR, C.FECHA_PROX_REVISION,
                       C.FECHA_MODIFICACION
                FROM GT_CONOCIMIENTO C
                JOIN GT_ORG_UNIDAD U ON U.ID_UNIDAD = C.ID_UNIDAD_DUENA
                JOIN GT_USUARIO P ON P.ID_USUARIO = C.ID_PROPIETARIO
                LEFT JOIN GT_USUARIO R ON R.ID_USUARIO = C.ID_REVISOR
                WHERE {' AND '.join(conditions)}
                ORDER BY C.FECHA_MODIFICACION DESC, C.TITULO
                """,
                binds,
            )
            return [
                {
                    "id": int(row[0]), "tipo": row[1], "titulo": row[2],
                    "resumen": row[3], "estado": row[4],
                    "clasificacion": row[5], "version": int(row[6]),
                    "unidad": row[7], "propietario": row[8], "revisor": row[9],
                    "fecha_prox_revision": row[10], "fecha_modificacion": row[11],
                }
                for row in cur.fetchall()
            ]


def get_document(document_id: int) -> dict:
    assert_document_access(document_id)
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT C.ID_CONOCIMIENTO, C.TIPO, C.TITULO, C.RESUMEN,
                       C.CONTENIDO, C.ETIQUETAS, C.ESTADO,
                       C.ID_UNIDAD_DUENA, U.NOMBRE,
                       C.ID_PROPIETARIO, P.NOMBRE,
                       C.ID_REVISOR, R.NOMBRE,
                       C.CLASIFICACION, C.VERSION_ACTUAL,
                       C.FECHA_VIGENCIA, C.FECHA_PROX_REVISION,
                       C.MOTIVO_ULTIMO_CAMBIO, C.FECHA_CREACION,
                       C.FECHA_MODIFICACION, C.ACTIVO
                FROM GT_CONOCIMIENTO C
                JOIN GT_ORG_UNIDAD U ON U.ID_UNIDAD = C.ID_UNIDAD_DUENA
                JOIN GT_USUARIO P ON P.ID_USUARIO = C.ID_PROPIETARIO
                LEFT JOIN GT_USUARIO R ON R.ID_USUARIO = C.ID_REVISOR
                WHERE C.ID_CONOCIMIENTO = :id
                """,
                {"id": int(document_id)},
            )
            document = _document_dict(cur.fetchone())
            if document is None:
                raise LookupError("Documento no encontrado.")

            cur.execute(
                """
                SELECT NUMERO_VERSION, TITULO, RESUMEN, MOTIVO_CAMBIO,
                       FECHA_VERSION, U.NOMBRE
                FROM GT_CONOCIMIENTO_VERSION V
                JOIN GT_USUARIO U ON U.ID_USUARIO = V.CREADO_POR
                WHERE V.ID_CONOCIMIENTO = :id
                ORDER BY NUMERO_VERSION DESC
                """,
                {"id": int(document_id)},
            )
            document["versiones"] = [
                {
                    "version": int(row[0]), "titulo": row[1], "resumen": row[2],
                    "motivo": row[3], "fecha": row[4], "autor": row[5],
                }
                for row in cur.fetchall()
            ]

            cur.execute(
                """
                SELECT TIPO_ENTIDAD, ID_ENTIDAD
                FROM GT_CONOCIMIENTO_RELACION
                WHERE ID_CONOCIMIENTO = :id AND ACTIVO = 'S'
                ORDER BY TIPO_ENTIDAD, ID_ENTIDAD
                """,
                {"id": int(document_id)},
            )
            document["relaciones"] = [
                {"tipo": row[0], "id_entidad": int(row[1])}
                for row in cur.fetchall()
            ]
    return document


def catalogs() -> tuple[list, list]:
    units_scope = accessible_unit_ids()
    with connection() as conn:
        with conn.cursor() as cur:
            if units_scope is None:
                cur.execute(
                    "SELECT ID_UNIDAD, CODIGO, NOMBRE FROM GT_ORG_UNIDAD WHERE ACTIVO='S' ORDER BY NOMBRE"
                )
                units = cur.fetchall()
                cur.execute(
                    "SELECT ID_USUARIO, NOMBRE FROM GT_USUARIO WHERE ACTIVO='S' ORDER BY NOMBRE"
                )
                users = cur.fetchall()
            else:
                placeholders, binds = in_clause(units_scope, prefix="knowledge_catalog")
                cur.execute(
                    f"SELECT ID_UNIDAD, CODIGO, NOMBRE FROM GT_ORG_UNIDAD "
                    f"WHERE ACTIVO='S' AND ID_UNIDAD IN ({placeholders}) ORDER BY NOMBRE",
                    binds,
                )
                units = cur.fetchall()
                cur.execute(
                    f"""
                    SELECT DISTINCT U.ID_USUARIO, U.NOMBRE
                    FROM GT_USUARIO U
                    JOIN GT_USUARIO_UNIDAD UU ON UU.ID_USUARIO=U.ID_USUARIO AND UU.ACTIVO='S'
                    WHERE U.ACTIVO='S' AND UU.ID_UNIDAD IN ({placeholders})
                    ORDER BY U.NOMBRE
                    """,
                    binds,
                )
                users = cur.fetchall()
    return units, users


def _insert_version(cur, document_id: int, version: int, payload: KnowledgePayload, estado: str, motivo: str, user_id: int) -> None:
    cur.execute(
        """
        INSERT INTO GT_CONOCIMIENTO_VERSION (
            ID_CONOCIMIENTO, NUMERO_VERSION, TITULO, RESUMEN, CONTENIDO,
            ETIQUETAS, ESTADO_ORIGEN, MOTIVO_CAMBIO, CREADO_POR
        ) VALUES (
            :id, :version, :titulo, :resumen, :contenido,
            :etiquetas, :estado, :motivo, :usuario
        )
        """,
        {
            "id": document_id, "version": version, "titulo": payload.titulo,
            "resumen": payload.resumen, "contenido": payload.contenido,
            "etiquetas": payload.etiquetas, "estado": estado,
            "motivo": motivo, "usuario": user_id,
        },
    )


def create_document(payload: KnowledgePayload) -> int:
    payload = normalize_payload(payload)
    user_id = int(session["id_usuario"])
    if payload.id_revisor == user_id:
        raise ValueError("El propietario no puede ser su propio revisor.")

    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            out_id = cur.var(int)
            cur.execute(
                """
                INSERT INTO GT_CONOCIMIENTO (
                    TIPO, TITULO, RESUMEN, CONTENIDO, ETIQUETAS, ESTADO,
                    ID_UNIDAD_DUENA, ID_PROPIETARIO, ID_REVISOR, CLASIFICACION,
                    VERSION_ACTUAL, FECHA_VIGENCIA, FECHA_PROX_REVISION,
                    MOTIVO_ULTIMO_CAMBIO, CREADO_POR, MODIFICADO_POR, ACTIVO
                ) VALUES (
                    :tipo, :titulo, :resumen, :contenido, :etiquetas, 'BORRADOR',
                    :unidad, :propietario, :revisor, :clasificacion,
                    1, :vigencia, :revision, :motivo, :usuario, :usuario, 'S'
                ) RETURNING ID_CONOCIMIENTO INTO :id
                """,
                {
                    "tipo": payload.tipo, "titulo": payload.titulo,
                    "resumen": payload.resumen, "contenido": payload.contenido,
                    "etiquetas": payload.etiquetas, "unidad": payload.id_unidad,
                    "propietario": user_id, "revisor": payload.id_revisor,
                    "clasificacion": payload.clasificacion,
                    "vigencia": payload.fecha_vigencia,
                    "revision": payload.fecha_prox_revision,
                    "motivo": payload.motivo or "Creación inicial",
                    "usuario": user_id, "id": out_id,
                },
            )
            document_id = int(out_id.getvalue()[0])
            _insert_version(
                cur, document_id, 1, payload, "BORRADOR",
                payload.motivo or "Creación inicial", user_id,
            )
            write_event(
                cur, "CONOCIMIENTO", "GT_CONOCIMIENTO", "INSERT", document_id,
                after={"estado": "BORRADOR", "version": 1, "titulo": payload.titulo},
            )
    return document_id


def update_document(document_id: int, payload: KnowledgePayload) -> int:
    access_doc = assert_document_access(document_id, edit=True)
    payload = normalize_payload(payload)
    user_id = int(session["id_usuario"])
    if payload.id_revisor == user_id and user_id == access_doc["id_propietario"]:
        raise ValueError("El propietario no puede ser su propio revisor.")

    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT VERSION_ACTUAL, ESTADO FROM GT_CONOCIMIENTO WHERE ID_CONOCIMIENTO=:id FOR UPDATE",
                {"id": int(document_id)},
            )
            row = cur.fetchone()
            if not row:
                raise LookupError("Documento no encontrado.")
            next_version = int(row[0]) + 1
            current_state = row[1]
            cur.execute(
                """
                UPDATE GT_CONOCIMIENTO
                   SET TIPO=:tipo, TITULO=:titulo, RESUMEN=:resumen,
                       CONTENIDO=:contenido, ETIQUETAS=:etiquetas,
                       ID_UNIDAD_DUENA=:unidad, ID_REVISOR=:revisor,
                       CLASIFICACION=:clasificacion, VERSION_ACTUAL=:version,
                       FECHA_VIGENCIA=:vigencia, FECHA_PROX_REVISION=:revision,
                       MOTIVO_ULTIMO_CAMBIO=:motivo,
                       FECHA_MODIFICACION=SYSTIMESTAMP, MODIFICADO_POR=:usuario
                 WHERE ID_CONOCIMIENTO=:id
                """,
                {
                    "tipo": payload.tipo, "titulo": payload.titulo,
                    "resumen": payload.resumen, "contenido": payload.contenido,
                    "etiquetas": payload.etiquetas, "unidad": payload.id_unidad,
                    "revisor": payload.id_revisor,
                    "clasificacion": payload.clasificacion,
                    "version": next_version, "vigencia": payload.fecha_vigencia,
                    "revision": payload.fecha_prox_revision,
                    "motivo": payload.motivo or "Actualización de contenido",
                    "usuario": user_id, "id": int(document_id),
                },
            )
            _insert_version(
                cur, int(document_id), next_version, payload, current_state,
                payload.motivo or "Actualización de contenido", user_id,
            )
            write_event(
                cur, "CONOCIMIENTO", "GT_CONOCIMIENTO", "UPDATE", document_id,
                before={"version": next_version - 1},
                after={"version": next_version, "titulo": payload.titulo},
            )
    return next_version


def transition_document(document_id: int, target_state: str, reason: str | None = None) -> None:
    target = str(target_state or "").strip().upper()
    reason = _text(reason, 1000) or f"Cambio de estado a {target}"
    doc = assert_document_access(document_id)
    current = doc["estado"]
    if target not in TRANSITIONS.get(current, set()):
        raise ValueError(f"Transición documental no válida: {current} → {target}.")

    user_id = int(session["id_usuario"])
    role = str(session.get("rol_codigo") or "").upper()
    owner = user_id == doc["id_propietario"]

    if target == "EN_REVISION":
        if not (owner or can_edit_document(doc) or role == "ADMIN"):
            raise PermissionError("No puede enviar este documento a revisión.")
        if doc["id_revisor"] is None and role != "ADMIN":
            raise ValueError("Debe asignar un revisor antes de enviar a revisión.")
    elif target in {"PUBLICADO", "OBSOLETO"} or current == "EN_REVISION":
        if not can_review_document(doc):
            raise PermissionError("No puede resolver la revisión de este documento.")
    elif target == "REQUIERE_ACTUALIZACION":
        if not (owner or can_review_document(doc)):
            raise PermissionError("No puede marcar este documento para actualización.")

    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE GT_CONOCIMIENTO
                   SET ESTADO=:estado, MOTIVO_ULTIMO_CAMBIO=:motivo,
                       FECHA_MODIFICACION=SYSTIMESTAMP, MODIFICADO_POR=:usuario
                 WHERE ID_CONOCIMIENTO=:id AND ESTADO=:estado_actual AND ACTIVO='S'
                """,
                {
                    "estado": target, "motivo": reason, "usuario": user_id,
                    "id": int(document_id), "estado_actual": current,
                },
            )
            if cur.rowcount != 1:
                raise RuntimeError("El documento cambió mientras se procesaba la transición.")
            write_event(
                cur, "CONOCIMIENTO", "GT_CONOCIMIENTO", "STATUS", document_id,
                before={"estado": current}, after={"estado": target, "motivo": reason},
            )


def add_relation(document_id: int, relation_type: str, entity_id: int) -> None:
    assert_document_access(document_id, edit=True)
    relation_type = str(relation_type or "").strip().upper()
    if relation_type not in RELATION_TYPES:
        raise ValueError("Tipo de relación no válido.")
    entity_id = int(entity_id)
    user_id = int(session["id_usuario"])

    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM GT_CONOCIMIENTO_RELACION
                WHERE ID_CONOCIMIENTO=:doc AND TIPO_ENTIDAD=:tipo
                  AND ID_ENTIDAD=:entidad AND ACTIVO='S'
                """,
                {"doc": int(document_id), "tipo": relation_type, "entidad": entity_id},
            )
            if int(cur.fetchone()[0]) > 0:
                return
            cur.execute(
                """
                INSERT INTO GT_CONOCIMIENTO_RELACION (
                    ID_CONOCIMIENTO, TIPO_ENTIDAD, ID_ENTIDAD, CREADO_POR, ACTIVO
                ) VALUES (:doc, :tipo, :entidad, :usuario, 'S')
                """,
                {"doc": int(document_id), "tipo": relation_type, "entidad": entity_id, "usuario": user_id},
            )
            write_event(
                cur, "CONOCIMIENTO", "GT_CONOCIMIENTO_RELACION", "INSERT", document_id,
                after={"tipo_entidad": relation_type, "id_entidad": entity_id},
            )
