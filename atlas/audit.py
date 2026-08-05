import json
from flask import request, session

from .db import connection


def record_event(modulo, entidad, accion, id_entidad=None, before=None, after=None):
    try:
        with connection(commit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO GT_AUDITORIA (
                        ID_USUARIO, MODULO, ENTIDAD, ID_ENTIDAD, ACCION,
                        DATOS_ANTERIORES, DATOS_NUEVOS, IP_ORIGEN
                    ) VALUES (
                        :id_usuario, :modulo, :entidad, :id_entidad, :accion,
                        :datos_anteriores, :datos_nuevos, :ip_origen
                    )
                    """,
                    {
                        "id_usuario": session.get("id_usuario"),
                        "modulo": modulo,
                        "entidad": entidad,
                        "id_entidad": None if id_entidad is None else str(id_entidad),
                        "accion": accion,
                        "datos_anteriores": None if before is None else json.dumps(before, default=str),
                        "datos_nuevos": None if after is None else json.dumps(after, default=str),
                        "ip_origen": request.headers.get("X-Forwarded-For", request.remote_addr),
                    },
                )
    except Exception:
        # La auditoria no debe derribar la operacion principal en la primera version.
        # En produccion se debe registrar este error en archivo de log.
        pass
