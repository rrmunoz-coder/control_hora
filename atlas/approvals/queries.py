from __future__ import annotations

from datetime import timedelta
from typing import Any

from ..access import accessible_unit_ids, in_clause
from ..db import connection
from .common import row_dict


def _reviewer_role(reviewer_id: int) -> str:
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT R.CODIGO
                FROM GT_USUARIO U
                JOIN GT_ROL R ON R.ID_ROL = U.ID_ROL
                WHERE U.ID_USUARIO = :id_usuario
                  AND U.ACTIVO = 'S'
                  AND R.ACTIVO = 'S'
                """,
                {"id_usuario": reviewer_id},
            )
            row = cur.fetchone()
    return str(row[0]).upper() if row else ""


def can_review_user(reviewer_id: int, owner_id: int, role_code: str | None = None) -> bool:
    role = str(role_code or _reviewer_role(reviewer_id)).upper()
    if role == "ADMIN":
        return True
    if role != "JEFE" or reviewer_id == owner_id:
        return False

    units = accessible_unit_ids(reviewer_id, role)
    if not units:
        return False
    placeholders, binds = in_clause(units, prefix="review_unit")
    binds.update({"owner_id": owner_id, "reviewer_id": reviewer_id})
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT COUNT(*)
                FROM GT_USUARIO U
                LEFT JOIN GT_USUARIO_UNIDAD UU
                  ON UU.ID_USUARIO = U.ID_USUARIO
                 AND UU.ACTIVO = 'S'
                WHERE U.ID_USUARIO = :owner_id
                  AND U.ACTIVO = 'S'
                  AND (
                      U.ID_JEFE = :reviewer_id
                      OR UU.ID_UNIDAD IN ({placeholders})
                  )
                """,
                binds,
            )
            return int(cur.fetchone()[0]) > 0


def list_pending(reviewer_id: int, role_code: str) -> list[dict[str, Any]]:
    role = str(role_code).upper()
    binds: dict[str, Any] = {"reviewer_id": reviewer_id}
    if role == "ADMIN":
        scope = "1 = 1"
    else:
        units = accessible_unit_ids(reviewer_id, role)
        placeholders, unit_binds = in_clause(units or set(), prefix="pending_unit")
        binds.update(unit_binds)
        scope = (
            "(U.ID_JEFE = :reviewer_id OR EXISTS ("
            "SELECT 1 FROM GT_USUARIO_UNIDAD UU "
            "WHERE UU.ID_USUARIO = U.ID_USUARIO AND UU.ACTIVO = 'S' "
            f"AND UU.ID_UNIDAD IN ({placeholders})))"
        )

    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    V.ID_VALIDACION,
                    U.NOMBRE AS USUARIO_NOMBRE,
                    U.USUARIO,
                    TO_CHAR(V.FECHA_DESDE, 'YYYY-MM-DD') AS FECHA_DESDE,
                    TO_CHAR(V.FECHA_HASTA, 'YYYY-MM-DD') AS FECHA_HASTA,
                    V.HORAS_DECLARADAS,
                    V.ESTADO,
                    TO_CHAR(V.FECHA_ENVIO, 'YYYY-MM-DD HH24:MI') AS FECHA_ENVIO,
                    OU.NOMBRE AS UNIDAD
                FROM GT_VALIDACION_PERIODO V
                JOIN GT_USUARIO U ON U.ID_USUARIO = V.ID_USUARIO
                LEFT JOIN GT_USUARIO_UNIDAD UU0
                  ON UU0.ID_USUARIO = U.ID_USUARIO
                 AND UU0.ES_PRINCIPAL = 'S'
                 AND UU0.ACTIVO = 'S'
                LEFT JOIN GT_ORG_UNIDAD OU ON OU.ID_UNIDAD = UU0.ID_UNIDAD
                WHERE V.TIPO_PERIODO = 'SEMANAL'
                  AND V.ESTADO = 'ENVIADO'
                  AND {scope}
                ORDER BY V.FECHA_ENVIO, U.NOMBRE
                """,
                binds,
            )
            columns = [item[0].lower() for item in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]


def get_validation_detail(validation_id: int) -> dict[str, Any] | None:
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    V.ID_VALIDACION, V.ID_USUARIO, U.NOMBRE AS USUARIO_NOMBRE,
                    U.USUARIO, V.FECHA_DESDE, V.FECHA_HASTA, V.ESTADO,
                    V.HORAS_DECLARADAS, V.COMENTARIO,
                    TO_CHAR(V.FECHA_ENVIO, 'YYYY-MM-DD HH24:MI') AS FECHA_ENVIO,
                    TO_CHAR(V.FECHA_VALIDACION, 'YYYY-MM-DD HH24:MI') AS FECHA_VALIDACION,
                    OU.NOMBRE AS UNIDAD
                FROM GT_VALIDACION_PERIODO V
                JOIN GT_USUARIO U ON U.ID_USUARIO = V.ID_USUARIO
                LEFT JOIN GT_USUARIO_UNIDAD UU
                  ON UU.ID_USUARIO = U.ID_USUARIO
                 AND UU.ES_PRINCIPAL = 'S' AND UU.ACTIVO = 'S'
                LEFT JOIN GT_ORG_UNIDAD OU ON OU.ID_UNIDAD = UU.ID_UNIDAD
                WHERE V.ID_VALIDACION = :id_validacion
                """,
                {"id_validacion": validation_id},
            )
            detail = row_dict(cur, cur.fetchone())
            if not detail:
                return None
            cur.execute(
                """
                SELECT
                    TO_CHAR(I.FECHA_TRABAJO, 'YYYY-MM-DD') AS FECHA,
                    T.CODIGO, T.TITULO, T.CLASIFICACION_COSTO,
                    I.HORAS, I.COMENTARIO
                FROM GT_IMPUTACION_HORAS I
                JOIN GT_TAREA T ON T.ID_TAREA = I.ID_TAREA
                WHERE I.ID_USUARIO = :id_usuario
                  AND I.FECHA_TRABAJO >= :fecha_desde
                  AND I.FECHA_TRABAJO < :fecha_hasta
                ORDER BY I.FECHA_TRABAJO, T.CODIGO
                """,
                {
                    "id_usuario": int(detail["id_usuario"]),
                    "fecha_desde": detail["fecha_desde"],
                    "fecha_hasta": detail["fecha_hasta"] + timedelta(days=1),
                },
            )
            columns = [item[0].lower() for item in cur.description]
            detail["entries"] = [dict(zip(columns, row)) for row in cur.fetchall()]
            return detail
