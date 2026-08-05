from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from werkzeug.security import check_password_hash

from ..db import connection
from .ldap_auth import LDAPStatus, authenticate_ldap


class AuthStatus(str, Enum):
    SUCCESS = "SUCCESS"
    INVALID = "INVALID"
    UNAVAILABLE = "UNAVAILABLE"
    CONFIG_ERROR = "CONFIG_ERROR"


@dataclass(frozen=True)
class AuthenticatedUser:
    id_usuario: int
    usuario: str
    nombre: str
    rol_codigo: str
    rol_nombre: str
    tipo_autenticacion: str


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
                    A.USUARIO_LDAP
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
                       FECHA_ACTUALIZACION = SYSTIMESTAMP
                 WHERE ID_USUARIO = :id_usuario
                """,
                {"id_usuario": id_usuario},
            )


def _record_failure(id_usuario: int) -> None:
    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE GT_USUARIO_AUTH
                   SET ULTIMO_LOGIN_FALLIDO = SYSTIMESTAMP,
                       INTENTOS_FALLIDOS = NVL(INTENTOS_FALLIDOS, 0) + 1,
                       FECHA_ACTUALIZACION = SYSTIMESTAMP
                 WHERE ID_USUARIO = :id_usuario
                """,
                {"id_usuario": id_usuario},
            )


def authenticate_atlas(username: str, password: str) -> AuthResult:
    row = _load_user(username)
    if not row:
        return AuthResult(AuthStatus.INVALID)

    id_usuario = int(row[0])
    tipo_auth = str(row[6] or "").upper()

    if tipo_auth == "LOCAL":
        password_hash = row[2]
        if not password_hash or not check_password_hash(password_hash, password):
            _record_failure(id_usuario)
            return AuthResult(AuthStatus.INVALID)

    elif tipo_auth == "LDAP":
        usuario_ldap = row[7]
        if not usuario_ldap:
            _record_failure(id_usuario)
            return AuthResult(
                AuthStatus.CONFIG_ERROR,
                technical_detail="Usuario LDAP sin USUARIO_LDAP configurado",
            )

        ldap_result = authenticate_ldap(usuario_ldap, password)

        if ldap_result.status == LDAPStatus.INVALID_CREDENTIALS:
            _record_failure(id_usuario)
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

    return AuthResult(
        AuthStatus.SUCCESS,
        user=AuthenticatedUser(
            id_usuario=id_usuario,
            usuario=row[1],
            nombre=row[3],
            rol_codigo=row[4],
            rol_nombre=row[5],
            tipo_autenticacion=tipo_auth,
        ),
    )
