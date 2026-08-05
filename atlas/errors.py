from __future__ import annotations

import logging
import uuid

import oracledb
from flask import flash, g

logger = logging.getLogger(__name__)


class UserFacingError(ValueError):
    """Error funcional cuyo mensaje puede mostrarse al usuario."""


def request_id() -> str:
    current = getattr(g, "request_id", None)
    if current:
        return str(current)
    current = uuid.uuid4().hex[:12]
    g.request_id = current
    return current


def oracle_message(exc: oracledb.DatabaseError) -> str | None:
    """Devuelve solo mensajes funcionales levantados por ATLAS (ORA-20xxx)."""
    if not exc.args:
        return None
    error = exc.args[0]
    code = abs(int(getattr(error, "code", 0) or 0))
    if code < 20000 or code > 20999:
        return None
    message = str(getattr(error, "message", exc)).strip()
    prefix = f"ORA-{code}:"
    if message.upper().startswith(prefix):
        message = message[len(prefix):].strip()
    return message.split("ORA-06512", 1)[0].strip()


def flash_exception(
    exc: Exception,
    *,
    context: str,
    generic_message: str = "No fue posible completar la operación.",
) -> str:
    """Registra el detalle técnico y muestra un mensaje seguro con correlación."""
    public_message: str | None = None
    if isinstance(exc, (UserFacingError, ValueError, LookupError)):
        public_message = str(exc).strip()
    elif isinstance(exc, oracledb.DatabaseError):
        public_message = oracle_message(exc)

    incident_id = request_id()
    if public_message:
        logger.warning(
            "%s: %s [incidente=%s]",
            context,
            public_message,
            incident_id,
        )
    else:
        logger.exception("%s [incidente=%s]", context, incident_id)
    if public_message:
        flash(public_message, "error")
    else:
        flash(f"{generic_message} Código de referencia: {incident_id}.", "error")
    return incident_id
