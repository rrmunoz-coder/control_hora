from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from ..audit import write_event
from ..db import connection
from ..errors import UserFacingError
from .common import EDITABLE_STATES, row_dict


def get_period(user_id: int, week_start: date) -> dict[str, Any]:
    week_end = week_start + timedelta(days=6)
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    V.ID_VALIDACION,
                    V.ID_USUARIO,
                    V.FECHA_DESDE,
                    V.FECHA_HASTA,
                    V.ESTADO,
                    V.HORAS_DECLARADAS,
                    V.ID_VALIDADOR,
                    TO_CHAR(V.FECHA_ENVIO, 'YYYY-MM-DD HH24:MI:SS') AS FECHA_ENVIO,
                    TO_CHAR(V.FECHA_VALIDACION, 'YYYY-MM-DD HH24:MI:SS') AS FECHA_VALIDACION,
                    V.COMENTARIO,
                    J.NOMBRE AS VALIDADOR_NOMBRE
                FROM GT_VALIDACION_PERIODO V
                LEFT JOIN GT_USUARIO J ON J.ID_USUARIO = V.ID_VALIDADOR
                WHERE V.ID_USUARIO = :id_usuario
                  AND V.TIPO_PERIODO = 'SEMANAL'
                  AND V.FECHA_DESDE = :fecha_desde
                  AND V.FECHA_HASTA = :fecha_hasta
                """,
                {
                    "id_usuario": user_id,
                    "fecha_desde": week_start,
                    "fecha_hasta": week_end,
                },
            )
            result = row_dict(cur, cur.fetchone())
    if result:
        result["editable"] = str(result["estado"]).upper() in EDITABLE_STATES
        return result
    return {
        "id_validacion": None,
        "id_usuario": user_id,
        "fecha_desde": week_start,
        "fecha_hasta": week_end,
        "estado": "PENDIENTE",
        "horas_declaradas": None,
        "id_validador": None,
        "fecha_envio": None,
        "fecha_validacion": None,
        "comentario": None,
        "validador_nombre": None,
        "editable": True,
    }


def assert_week_editable(user_id: int, week_start: date) -> dict[str, Any]:
    period = get_period(user_id, week_start)
    if str(period["estado"]).upper() not in EDITABLE_STATES:
        raise UserFacingError(
            "La semana ya fue enviada o aprobada y no puede modificarse."
        )
    return period


def submit_period(user_id: int, week_start: date) -> dict[str, Any]:
    week_end = week_start + timedelta(days=6)
    with connection(commit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ID_VALIDACION, ESTADO
                FROM GT_VALIDACION_PERIODO
                WHERE ID_USUARIO = :id_usuario
                  AND TIPO_PERIODO = 'SEMANAL'
                  AND FECHA_DESDE = :fecha_desde
                  AND FECHA_HASTA = :fecha_hasta
                FOR UPDATE
                """,
                {
                    "id_usuario": user_id,
                    "fecha_desde": week_start,
                    "fecha_hasta": week_end,
                },
            )
            existing = cur.fetchone()
            if existing and str(existing[1]).upper() not in EDITABLE_STATES:
                raise UserFacingError("La semana ya fue enviada o aprobada.")

            cur.execute(
                """
                SELECT COUNT(DISTINCT FECHA_DIA)
                FROM GT_CALENDARIO_PERSONA
                WHERE ID_USUARIO = :id_usuario
                  AND FECHA_DIA >= :fecha_desde
                  AND FECHA_DIA < :fecha_hasta
                """,
                {
                    "id_usuario": user_id,
                    "fecha_desde": week_start,
                    "fecha_hasta": week_end + timedelta(days=1),
                },
            )
            if int(cur.fetchone()[0]) < 7:
                raise UserFacingError(
                    "Guarda primero la semana completa y sus modalidades antes de enviarla."
                )

            cur.execute(
                """
                SELECT NVL(SUM(HORAS), 0)
                FROM GT_IMPUTACION_HORAS
                WHERE ID_USUARIO = :id_usuario
                  AND FECHA_TRABAJO >= :fecha_desde
                  AND FECHA_TRABAJO < :fecha_hasta
                """,
                {
                    "id_usuario": user_id,
                    "fecha_desde": week_start,
                    "fecha_hasta": week_end + timedelta(days=1),
                },
            )
            total = float(cur.fetchone()[0] or 0)

            cur.execute(
                "SELECT ID_JEFE FROM GT_USUARIO WHERE ID_USUARIO = :id_usuario",
                {"id_usuario": user_id},
            )
            boss_row = cur.fetchone()
            validator_id = int(boss_row[0]) if boss_row and boss_row[0] is not None else None

            if existing:
                validation_id = int(existing[0])
                cur.execute(
                    """
                    UPDATE GT_VALIDACION_PERIODO
                       SET ESTADO = 'ENVIADO',
                           HORAS_DECLARADAS = :horas,
                           ID_VALIDADOR = :id_validador,
                           FECHA_ENVIO = SYSTIMESTAMP,
                           FECHA_VALIDACION = NULL,
                           COMENTARIO = NULL
                     WHERE ID_VALIDACION = :id_validacion
                    """,
                    {
                        "horas": total,
                        "id_validador": validator_id,
                        "id_validacion": validation_id,
                    },
                )
            else:
                out_id = cur.var(int)
                cur.execute(
                    """
                    INSERT INTO GT_VALIDACION_PERIODO (
                        ID_USUARIO, TIPO_PERIODO, FECHA_DESDE, FECHA_HASTA,
                        ESTADO, HORAS_DECLARADAS, ID_VALIDADOR, FECHA_ENVIO
                    ) VALUES (
                        :id_usuario, 'SEMANAL', :fecha_desde, :fecha_hasta,
                        'ENVIADO', :horas, :id_validador, SYSTIMESTAMP
                    ) RETURNING ID_VALIDACION INTO :id_validacion
                    """,
                    {
                        "id_usuario": user_id,
                        "fecha_desde": week_start,
                        "fecha_hasta": week_end,
                        "horas": total,
                        "id_validador": validator_id,
                        "id_validacion": out_id,
                    },
                )
                validation_id = int(out_id.getvalue()[0])

            cur.execute(
                """
                UPDATE GT_IMPUTACION_HORAS
                   SET ESTADO = 'ENVIADA',
                       FECHA_ACTUALIZACION = SYSTIMESTAMP,
                       ACTUALIZADO_POR = :id_usuario
                 WHERE ID_USUARIO = :id_usuario
                   AND FECHA_TRABAJO >= :fecha_desde
                   AND FECHA_TRABAJO < :fecha_hasta
                """,
                {
                    "id_usuario": user_id,
                    "fecha_desde": week_start,
                    "fecha_hasta": week_end + timedelta(days=1),
                },
            )
            audit_result = {
                "id_validacion": validation_id,
                "estado": "ENVIADO",
                "horas_declaradas": total,
                "id_validador": validator_id,
                "fecha_desde": week_start.isoformat(),
                "fecha_hasta": week_end.isoformat(),
            }
            write_event(
                cur,
                "APROBACIONES",
                "GT_VALIDACION_PERIODO",
                "ENVIAR",
                validation_id,
                after=audit_result,
                user_id=user_id,
            )

    return {
        "id_validacion": validation_id,
        "estado": "ENVIADO",
        "horas_declaradas": total,
        "id_validador": validator_id,
        "fecha_desde": week_start.isoformat(),
        "fecha_hasta": week_end.isoformat(),
    }
