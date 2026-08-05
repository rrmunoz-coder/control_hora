from __future__ import annotations

from ..db import connection


def revoke_sessions(user_id: int) -> None:
    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE GT_USUARIO_AUTH
                   SET SESSION_VERSION = NVL(SESSION_VERSION, 1) + 1,
                       FECHA_ACTUALIZACION = SYSTIMESTAMP
                 WHERE ID_USUARIO = :id_usuario
                """,
                {"id_usuario": user_id},
            )


def reset_failed_attempts_secure(user_id: int) -> None:
    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE GT_USUARIO_AUTH
                   SET INTENTOS_FALLIDOS = 0,
                       BLOQUEADO_HASTA = NULL,
                       FECHA_ACTUALIZACION = SYSTIMESTAMP
                 WHERE ID_USUARIO = :id_usuario
                """,
                {"id_usuario": user_id},
            )
