from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from flask import current_app
from werkzeug.security import check_password_hash

from ..db import connection
from .ldap_auth import LDAPStatus, authenticate_ldap


class AuthStatus(str, Enum):
    SUCCESS = "SUCCESS"
    INVALID = "INVALID"
    UNAVAILABLE = "UNAVAILABLE"
    CONFIG_ERROR = "CONFIG_ERROR"
    LOCKED = "LOCKED"


@dataclass(frozen=True)
class AuthenticatedUser:
    id_usuario: int
    usuario: str
    nombre: str
    rol_codigo: str
    rol_nombre: str
    tipo_autenticacion: str
    session_version: int


@dataclass(frozen=True)
class AuthResult:
    status: AuthStatus
    user: AuthenticatedUser | None = None
    technical_detail: str | None = None


def _load_user(username: str):
    """
    La identidad, rol y estado se leen desde GT_USUARIO/GT_ROL.
    El método de autenticación se lee desde GT_USUARIO_AUTH.

    El INNER JOIN a GT_USUARIO_AUTH es intencional:
    una persona no puede entrar si no está inscrita en la tabla de control.
    """
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    U.ID_USUARIO,
                    U.USUARIO,
                    U.PASSWORD_HASH,
                    U.NOMBRE,
                    R.CODIGO AS ROL_CODIGO,
                    R.NOMBRE AS ROL_NOMBRE,
                    A.TIPO_AUTENTICACION,
                    A.USUARIO_LDAP,
                    NVL(A.SESSION_VERSION, 1) AS SESSION_VERSION,
                    CASE
                        WHEN A.BLOQUEADO_HASTA > SYSTIMESTAMP THEN 'S'
                        ELSE 'N'
                    END AS ESTA_BLOQUEADO,
                    NVL(A.INTENTOS_FALLIDOS, 0) AS INTENTOS_FALLIDOS
                FROM GT_USUARIO U
                JOIN GT_ROL R
                  ON R.ID_ROL = U.ID_ROL
                JOIN GT_USUARIO_AUTH A
                  ON A.ID_USUARIO = U.ID_USUARIO
                WHERE UPPER(U.USUARIO) = UPPER(:usuario)
                  AND U.ACTIVO = 'S'
                  AND R.ACTIVO = 'S'
                """,
                {"usuario": username},
            )
            return cur.fetchone()


def _record_success(id_usuario: int) -> None:
    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE GT_USUARIO_AUTH
                   SET ULTIMO_LOGIN_EXITO = SYSTIMESTAMP,
                       INTENTOS_FALLIDOS = 0,
                       BLOQUEADO_HASTA = NULL,
                       FECHA_ACTUALIZACION = SYSTIMESTAMP
                 WHERE ID_USUARIO = :id_usuario
                """,
                {"id_usuario": id_usuario},
            )


def _record_failure(id_usuario: int) -> None:
    max_attempts = int(current_app.config.get("MAX_FAILED_LOGINS", 5))
    lock_minutes = int(current_app.config.get("LOGIN_LOCK_MINUTES", 15))
    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE GT_USUARIO_AUTH
                   SET ULTIMO_LOGIN_FALLIDO = SYSTIMESTAMP,
                       INTENTOS_FALLIDOS = NVL(INTENTOS_FALLIDOS, 0) + 1,
                       BLOQUEADO_HASTA =
                           CASE
                               WHEN NVL(INTENTOS_FALLIDOS, 0) + 1 >= :max_attempts
                               THEN SYSTIMESTAMP + NUMTODSINTERVAL(:lock_minutes, 'MINUTE')
                               ELSE BLOQUEADO_HASTA
                           END,
                       FECHA_ACTUALIZACION = SYSTIMESTAMP
                 WHERE ID_USUARIO = :id_usuario
                """,
                {
                    "id_usuario": id_usuario,
                    "max_attempts": max_attempts,
                    "lock_minutes": lock_minutes,
                },
            )



def _normalize_origin_ip(origin_ip: str | None) -> str:
    value = (origin_ip or "UNKNOWN").strip()
    return value[:64] or "UNKNOWN"


def _ip_is_blocked(origin_ip: str | None) -> bool:
    normalized = _normalize_origin_ip(origin_ip)
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT CASE
                           WHEN BLOQUEADO_HASTA > SYSTIMESTAMP THEN 'S'
                           ELSE 'N'
                       END
                FROM GT_LOGIN_RATE_LIMIT
                WHERE IP_ORIGEN = :ip_origen
                """,
                {"ip_origen": normalized},
            )
            row = cur.fetchone()
    return bool(row and str(row[0]).upper() == "S")


def _record_ip_failure(origin_ip: str | None) -> None:
    normalized = _normalize_origin_ip(origin_ip)
    max_attempts = int(current_app.config.get("MAX_FAILED_LOGINS_IP", 20))
    window_minutes = int(current_app.config.get("LOGIN_RATE_WINDOW_MINUTES", 15))
    lock_minutes = int(current_app.config.get("LOGIN_LOCK_MINUTES", 15))
    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                MERGE INTO GT_LOGIN_RATE_LIMIT L
                USING (SELECT :ip_origen AS IP_ORIGEN FROM DUAL) S
                   ON (L.IP_ORIGEN = S.IP_ORIGEN)
                WHEN MATCHED THEN UPDATE SET
                    L.INTENTOS_FALLIDOS =
                        CASE
                            WHEN L.VENTANA_INICIO <
                                 SYSTIMESTAMP - NUMTODSINTERVAL(:window_minutes, 'MINUTE')
                            THEN 1
                            ELSE NVL(L.INTENTOS_FALLIDOS, 0) + 1
                        END,
                    L.VENTANA_INICIO =
                        CASE
                            WHEN L.VENTANA_INICIO <
                                 SYSTIMESTAMP - NUMTODSINTERVAL(:window_minutes, 'MINUTE')
                            THEN SYSTIMESTAMP
                            ELSE L.VENTANA_INICIO
                        END,
                    L.BLOQUEADO_HASTA =
                        CASE
                            WHEN (
                                CASE
                                    WHEN L.VENTANA_INICIO <
                                         SYSTIMESTAMP - NUMTODSINTERVAL(:window_minutes, 'MINUTE')
                                    THEN 1
                                    ELSE NVL(L.INTENTOS_FALLIDOS, 0) + 1
                                END
                            ) >= :max_attempts
                            THEN SYSTIMESTAMP + NUMTODSINTERVAL(:lock_minutes, 'MINUTE')
                            ELSE L.BLOQUEADO_HASTA
                        END,
                    L.FECHA_ACTUALIZACION = SYSTIMESTAMP
                WHEN NOT MATCHED THEN INSERT (
                    IP_ORIGEN, INTENTOS_FALLIDOS, VENTANA_INICIO, FECHA_ACTUALIZACION
                ) VALUES (
                    :ip_origen, 1, SYSTIMESTAMP, SYSTIMESTAMP
                )
                """,
                {
                    "ip_origen": normalized,
                    "window_minutes": window_minutes,
                    "max_attempts": max_attempts,
                    "lock_minutes": lock_minutes,
                },
            )


def _record_ip_success(origin_ip: str | None) -> None:
    normalized = _normalize_origin_ip(origin_ip)
    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM GT_LOGIN_RATE_LIMIT WHERE IP_ORIGEN = :ip_origen",
                {"ip_origen": normalized},
            )


def authenticate_atlas(
    username: str,
    password: str,
    origin_ip: str | None = None,
) -> AuthResult:
    if _ip_is_blocked(origin_ip):
        return AuthResult(AuthStatus.LOCKED)

    row = _load_user(username)
    if not row:
        _record_ip_failure(origin_ip)
        return AuthResult(AuthStatus.INVALID)

    id_usuario = int(row[0])
    tipo_auth = str(row[6] or "").upper()
    if str(row[9] or "N").upper() == "S":
        return AuthResult(AuthStatus.LOCKED)

    if tipo_auth == "LOCAL":
        password_hash = row[2]
        if not password_hash or not check_password_hash(password_hash, password):
            _record_failure(id_usuario)
            _record_ip_failure(origin_ip)
            return AuthResult(AuthStatus.INVALID)

    elif tipo_auth == "LDAP":
        usuario_ldap = row[7]
        if not usuario_ldap:
            _record_failure(id_usuario)
            _record_ip_failure(origin_ip)
            return AuthResult(
                AuthStatus.CONFIG_ERROR,
                technical_detail="Usuario LDAP sin USUARIO_LDAP configurado",
            )

        ldap_result = authenticate_ldap(usuario_ldap, password)

        if ldap_result.status == LDAPStatus.INVALID_CREDENTIALS:
            _record_failure(id_usuario)
            _record_ip_failure(origin_ip)
            return AuthResult(AuthStatus.INVALID)

        if ldap_result.status == LDAPStatus.UNAVAILABLE:
            return AuthResult(
                AuthStatus.UNAVAILABLE,
                technical_detail=ldap_result.detail,
            )

        if ldap_result.status == LDAPStatus.CONFIG_ERROR:
            return AuthResult(
                AuthStatus.CONFIG_ERROR,
                technical_detail=ldap_result.detail,
            )

    else:
        return AuthResult(
            AuthStatus.CONFIG_ERROR,
            technical_detail=f"TIPO_AUTENTICACION no soportado: {tipo_auth}",
        )

    _record_success(id_usuario)
    _record_ip_success(origin_ip)

    return AuthResult(
        AuthStatus.SUCCESS,
        user=AuthenticatedUser(
            id_usuario=id_usuario,
            usuario=row[1],
            nombre=row[3],
            rol_codigo=row[4],
            rol_nombre=row[5],
            tipo_autenticacion=tipo_auth,
            session_version=int(row[8] or 1),
        ),
    )
