from __future__ import annotations

from datetime import timedelta
from typing import Any

from ..audit import write_event
from ..db import connection
from ..errors import UserFacingError
from .common import REVIEW_ACTIONS
from .queries import can_review_user, get_validation_detail


def review_period(
    reviewer_id: int,
    role_code: str,
    validation_id: int,
    action: str,
    comment: str | None,
) -> dict[str, Any]:
    normalized_action = str(action).upper()
    if normalized_action not in REVIEW_ACTIONS:
        raise UserFacingError("Acción de validación no permitida.")
    clean_comment = (comment or "").strip()
    if normalized_action in {"OBSERVAR", "RECHAZAR"} and not clean_comment:
        raise UserFacingError("Debes indicar el motivo de la observación o rechazo.")
    if len(clean_comment) > 2000:
        raise UserFacingError("El comentario no puede superar 2.000 caracteres.")

    detail = get_validation_detail(validation_id)
    if not detail:
        raise LookupError("La validación no existe.")
    owner_id = int(detail["id_usuario"])
    if not can_review_user(reviewer_id, owner_id, role_code):
        from flask import abort
        abort(403)

    target_state = REVIEW_ACTIONS[normalized_action]
    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ESTADO
                FROM GT_VALIDACION_PERIODO
                WHERE ID_VALIDACION = :id_validacion
                FOR UPDATE
                """,
                {"id_validacion": validation_id},
            )
            row = cur.fetchone()
            if not row or str(row[0]).upper() != "ENVIADO":
                raise UserFacingError("La semana ya no está pendiente de validación.")
            cur.execute(
                """
                UPDATE GT_VALIDACION_PERIODO
                   SET ESTADO = :estado,
                       ID_VALIDADOR = :id_validador,
                       FECHA_VALIDACION = SYSTIMESTAMP,
                       COMENTARIO = :comentario
                 WHERE ID_VALIDACION = :id_validacion
                """,
                {
                    "estado": target_state,
                    "id_validador": reviewer_id,
                    "comentario": clean_comment or None,
                    "id_validacion": validation_id,
                },
            )
            entry_state = "APROBADA" if target_state == "APROBADO" else "REGISTRADA"
            cur.execute(
                """
                UPDATE GT_IMPUTACION_HORAS
                   SET ESTADO = :estado,
                       FECHA_ACTUALIZACION = SYSTIMESTAMP,
                       ACTUALIZADO_POR = :id_validador
                 WHERE ID_USUARIO = :id_usuario
                   AND FECHA_TRABAJO >= :fecha_desde
                   AND FECHA_TRABAJO < :fecha_hasta
                """,
                {
                    "estado": entry_state,
                    "id_validador": reviewer_id,
                    "id_usuario": owner_id,
                    "fecha_desde": detail["fecha_desde"],
                    "fecha_hasta": detail["fecha_hasta"] + timedelta(days=1),
                },
            )
            write_event(
                cur,
                "APROBACIONES",
                "GT_VALIDACION_PERIODO",
                normalized_action,
                validation_id,
                before={"estado": "ENVIADO"},
                after={
                    "estado": target_state,
                    "id_usuario": owner_id,
                    "comentario": clean_comment or None,
                },
                user_id=reviewer_id,
            )
    return {
        "id_validacion": validation_id,
        "id_usuario": owner_id,
        "estado": target_state,
        "comentario": clean_comment or None,
    }


def reopen_period(
    reviewer_id: int,
    role_code: str,
    validation_id: int,
    comment: str | None,
) -> dict[str, Any]:
    if str(role_code).upper() != "ADMIN":
        from flask import abort
        abort(403)
    clean_comment = (comment or "").strip()
    if not clean_comment:
        raise UserFacingError("Debes indicar el motivo de reapertura.")
    detail = get_validation_detail(validation_id)
    if not detail:
        raise LookupError("La validación no existe.")
    previous_state = str(detail["estado"]).upper()
    if previous_state not in {"APROBADO", "CERRADO"}:
        raise UserFacingError("Solo se pueden reabrir semanas aprobadas o cerradas.")

    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE GT_VALIDACION_PERIODO
                   SET ESTADO = 'REABIERTO',
                       ID_VALIDADOR = :id_validador,
                       FECHA_VALIDACION = SYSTIMESTAMP,
                       COMENTARIO = :comentario
                 WHERE ID_VALIDACION = :id_validacion
                   AND ESTADO IN ('APROBADO', 'CERRADO')
                """,
                {
                    "id_validador": reviewer_id,
                    "comentario": clean_comment[:2000],
                    "id_validacion": validation_id,
                },
            )
            if cur.rowcount != 1:
                raise UserFacingError("La semana cambió de estado y no pudo reabrirse.")
            cur.execute(
                """
                UPDATE GT_IMPUTACION_HORAS
                   SET ESTADO = 'REGISTRADA',
                       FECHA_ACTUALIZACION = SYSTIMESTAMP,
                       ACTUALIZADO_POR = :id_validador
                 WHERE ID_USUARIO = :id_usuario
                   AND FECHA_TRABAJO >= :fecha_desde
                   AND FECHA_TRABAJO < :fecha_hasta
                """,
                {
                    "id_validador": reviewer_id,
                    "id_usuario": int(detail["id_usuario"]),
                    "fecha_desde": detail["fecha_desde"],
                    "fecha_hasta": detail["fecha_hasta"] + timedelta(days=1),
                },
            )
            write_event(
                cur,
                "APROBACIONES",
                "GT_VALIDACION_PERIODO",
                "REABRIR",
                validation_id,
                before={"estado": previous_state},
                after={"estado": "REABIERTO", "comentario": clean_comment[:2000]},
                user_id=reviewer_id,
            )
    return {
        "id_validacion": validation_id,
        "id_usuario": int(detail["id_usuario"]),
        "estado": "REABIERTO",
        "comentario": clean_comment[:2000],
    }


def close_period(
    reviewer_id: int,
    role_code: str,
    validation_id: int,
    comment: str | None = None,
) -> dict[str, Any]:
    if str(role_code).upper() != "ADMIN":
        from flask import abort
        abort(403)

    clean_comment = (comment or "").strip()
    if len(clean_comment) > 2000:
        raise UserFacingError("El comentario no puede superar 2.000 caracteres.")

    detail = get_validation_detail(validation_id)
    if not detail:
        raise LookupError("La validación no existe.")
    if str(detail["estado"]).upper() != "APROBADO":
        raise UserFacingError("Solo se pueden cerrar semanas aprobadas.")

    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE GT_VALIDACION_PERIODO
                   SET ESTADO = 'CERRADO',
                       ID_VALIDADOR = :id_validador,
                       FECHA_VALIDACION = SYSTIMESTAMP,
                       COMENTARIO = COALESCE(:comentario, COMENTARIO)
                 WHERE ID_VALIDACION = :id_validacion
                   AND ESTADO = 'APROBADO'
                """,
                {
                    "id_validador": reviewer_id,
                    "comentario": clean_comment or None,
                    "id_validacion": validation_id,
                },
            )
            if cur.rowcount != 1:
                raise UserFacingError("La semana cambió de estado y no pudo cerrarse.")
            write_event(
                cur,
                "APROBACIONES",
                "GT_VALIDACION_PERIODO",
                "CERRAR",
                validation_id,
                before={"estado": "APROBADO"},
                after={"estado": "CERRADO", "comentario": clean_comment or None},
                user_id=reviewer_id,
            )

    return {
        "id_validacion": validation_id,
        "id_usuario": int(detail["id_usuario"]),
        "estado": "CERRADO",
        "comentario": clean_comment or None,
    }
