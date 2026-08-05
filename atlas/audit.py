from __future__ import annotations

import json
import logging
from typing import Any

from flask import current_app, request, session

from .db import connection

logger = logging.getLogger(__name__)


def origin_ip() -> str | None:
    """Dirección de origen ya normalizada por ProxyFix cuando corresponde."""
    if current_app.config.get("TRUST_PROXY_HEADERS"):
        return request.remote_addr
    return request.environ.get("REMOTE_ADDR")


def _payload(
    modulo: Any,
    entidad: Any,
    accion: Any,
    id_entidad: Any = None,
    before: Any = None,
    after: Any = None,
    *,
    user_id: int | None = None,
    ip_address: str | None = None,
) -> dict[str, Any]:
    return {
        "id_usuario": user_id if user_id is not None else session.get("id_usuario"),
        "modulo": str(modulo)[:60],
        "entidad": str(entidad)[:60],
        "id_entidad": None if id_entidad is None else str(id_entidad)[:100],
        "accion": str(accion).upper()[:30],
        "datos_anteriores": (
            None
            if before is None
            else json.dumps(before, default=str, ensure_ascii=False)
        ),
        "datos_nuevos": (
            None
            if after is None
            else json.dumps(after, default=str, ensure_ascii=False)
        ),
        "ip_origen": ip_address if ip_address is not None else origin_ip(),
    }


def write_event(
    cursor,
    modulo: Any,
    entidad: Any,
    accion: Any,
    id_entidad: Any = None,
    before: Any = None,
    after: Any = None,
    *,
    user_id: int | None = None,
    ip_address: str | None = None,
) -> None:
    """Escribe auditoría usando la transacción activa del llamador."""
    cursor.execute(
        """
        INSERT INTO GT_AUDITORIA (
            ID_USUARIO, MODULO, ENTIDAD, ID_ENTIDAD, ACCION,
            DATOS_ANTERIORES, DATOS_NUEVOS, IP_ORIGEN
        ) VALUES (
            :id_usuario, :modulo, :entidad, :id_entidad, :accion,
            :datos_anteriores, :datos_nuevos, :ip_origen
        )
        """,
        _payload(
            modulo,
            entidad,
            accion,
            id_entidad,
            before,
            after,
            user_id=user_id,
            ip_address=ip_address,
        ),
    )


def record_event(
    modulo: Any,
    entidad: Any,
    accion: Any,
    id_entidad: Any = None,
    before: Any = None,
    after: Any = None,
    *,
    critical: bool = False,
) -> bool:
    """
    Registra un evento en su propia transacción.

    Para acciones cuyo dato y auditoría deban ser atómicos, usar ``write_event``
    dentro de la misma conexión de negocio. ``critical=True`` se reserva para
    operaciones donde el llamador acepta abortar si la auditoría independiente
    no puede escribirse.
    """
    try:
        with connection(commit=True) as conn:
            with conn.cursor() as cur:
                write_event(
                    cur,
                    modulo,
                    entidad,
                    accion,
                    id_entidad,
                    before,
                    after,
                )
        return True
    except Exception:
        logger.exception(
            "Fallo de auditoría modulo=%s entidad=%s accion=%s id=%s",
            modulo,
            entidad,
            accion,
            id_entidad,
        )
        if critical:
            raise
        return False
