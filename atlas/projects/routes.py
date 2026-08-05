from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..access import accessible_unit_ids, assert_unit_access, in_clause
from ..audit import record_event
from ..db import connection
from ..errors import flash_exception
from ..security import login_required, roles_required
from ..utils import parse_date, parse_decimal

bp = Blueprint("projects", __name__, url_prefix="/proyectos")


def _scope_condition(column: str, *, include_responsible: bool = True):
    units = accessible_unit_ids()
    if units is None:
        return "1 = 1", {}
    placeholders, binds = in_clause(units, prefix="project_unit")
    condition = f"{column} IN ({placeholders})"
    if include_responsible:
        condition = f"({condition} OR P.ID_RESPONSABLE = :current_user)"
        binds["current_user"] = int(session["id_usuario"])
    return condition, binds


def _catalogs():
    units_scope = accessible_unit_ids()
    with connection() as conn:
        with conn.cursor() as cur:
            if units_scope is None:
                cur.execute(
                    """
                    SELECT ID_UNIDAD, CODIGO, NOMBRE, TIPO_UNIDAD
                    FROM GT_ORG_UNIDAD
                    WHERE ACTIVO = 'S'
                    ORDER BY TIPO_UNIDAD, NOMBRE
                    """
                )
                units = cur.fetchall()
                cur.execute(
                    """
                    SELECT ID_USUARIO, NOMBRE
                    FROM GT_USUARIO
                    WHERE ACTIVO = 'S'
                    ORDER BY NOMBRE
                    """
                )
                users = cur.fetchall()
            else:
                placeholders, binds = in_clause(units_scope, prefix="catalog_unit")
                cur.execute(
                    f"""
                    SELECT ID_UNIDAD, CODIGO, NOMBRE, TIPO_UNIDAD
                    FROM GT_ORG_UNIDAD
                    WHERE ACTIVO = 'S'
                      AND ID_UNIDAD IN ({placeholders})
                    ORDER BY TIPO_UNIDAD, NOMBRE
                    """,
                    binds,
                )
                units = cur.fetchall()
                cur.execute(
                    f"""
                    SELECT DISTINCT U.ID_USUARIO, U.NOMBRE
                    FROM GT_USUARIO U
                    JOIN GT_USUARIO_UNIDAD UU
                      ON UU.ID_USUARIO = U.ID_USUARIO
                     AND UU.ACTIVO = 'S'
                    WHERE U.ACTIVO = 'S'
                      AND UU.ID_UNIDAD IN ({placeholders})
                    ORDER BY U.NOMBRE
                    """,
                    binds,
                )
                users = cur.fetchall()
    return units, users


@bp.route("")
@login_required
def list_projects():
    condition, binds = _scope_condition("P.ID_UNIDAD_DUENA")
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    P.ID_PROYECTO,
                    P.CODIGO,
                    P.NOMBRE,
                    U.NOMBRE AS UNIDAD,
                    R.NOMBRE AS RESPONSABLE,
                    P.CLASIFICACION_COSTO,
                    P.ESTADO,
                    TO_CHAR(P.FECHA_INICIO, 'YYYY-MM-DD'),
                    TO_CHAR(P.FECHA_FIN, 'YYYY-MM-DD'),
                    P.PERMITE_IMPUTACION,
                    P.ACTIVO
                FROM GT_PROYECTO P
                JOIN GT_ORG_UNIDAD U ON U.ID_UNIDAD = P.ID_UNIDAD_DUENA
                LEFT JOIN GT_USUARIO R ON R.ID_USUARIO = P.ID_RESPONSABLE
                WHERE {condition}
                ORDER BY P.FECHA_INICIO DESC, P.CODIGO
                """,
                binds,
            )
            rows = cur.fetchall()
    return render_template("projects/list.html", projects=rows)


@bp.route("/nuevo", methods=["GET", "POST"])
@roles_required("ADMIN", "JEFE")
def create_project():
    units, users = _catalogs()

    if request.method == "POST":
        try:
            unit_id = int(request.form["id_unidad"])
            assert_unit_access(unit_id, manage=True)
            start_date = parse_date(request.form.get("fecha_inicio"), "Fecha de inicio")
            end_date = parse_date(request.form.get("fecha_fin"), "Fecha de fin")
            if end_date < start_date:
                raise ValueError("La fecha de fin no puede ser anterior a la fecha de inicio.")

            estimated = request.form.get("horas_estimadas", "").strip()
            estimated_value = None if not estimated else parse_decimal(estimated, "Horas estimadas")
            if estimated_value is not None and estimated_value < 0:
                raise ValueError("Las horas estimadas no pueden ser negativas.")

            responsible_id = int(request.form["id_responsable"]) if request.form.get("id_responsable") else None
            if responsible_id and responsible_id not in {int(row[0]) for row in users}:
                from flask import abort
                abort(403)

            with connection(commit=True) as conn:
                with conn.cursor() as cur:
                    out_id = cur.var(int)
                    cur.execute(
                        """
                        INSERT INTO GT_PROYECTO (
                            CODIGO, NOMBRE, DESCRIPCION, ID_UNIDAD_DUENA,
                            ID_RESPONSABLE, CLASIFICACION_COSTO, ESTADO,
                            FECHA_INICIO, FECHA_FIN, HORAS_ESTIMADAS,
                            PERMITE_IMPUTACION, ACTIVO
                        ) VALUES (
                            :codigo, :nombre, :descripcion, :id_unidad,
                            :id_responsable, :clasificacion, :estado,
                            :fecha_inicio, :fecha_fin, :horas_estimadas,
                            :permite_imputacion, 'S'
                        ) RETURNING ID_PROYECTO INTO :id_proyecto
                        """,
                        {
                            "codigo": request.form.get("codigo", "").strip().upper(),
                            "nombre": request.form.get("nombre", "").strip(),
                            "descripcion": request.form.get("descripcion") or None,
                            "id_unidad": unit_id,
                            "id_responsable": responsible_id,
                            "clasificacion": request.form["clasificacion_costo"],
                            "estado": request.form["estado"],
                            "fecha_inicio": start_date,
                            "fecha_fin": end_date,
                            "horas_estimadas": estimated_value,
                            "permite_imputacion": request.form.get("permite_imputacion", "N"),
                            "id_proyecto": out_id,
                        },
                    )
                    project_id = int(out_id.getvalue()[0])
                    cur.execute(
                        """
                        INSERT INTO GT_TAREA (
                            CODIGO, TITULO, DESCRIPCION, ID_PROYECTO,
                            ID_UNIDAD_DUENA, CLASIFICACION_COSTO, ESTADO,
                            PRIORIDAD, FECHA_INICIO, FECHA_COMPROMISO,
                            HORAS_ESTIMADAS, PERMITE_IMPUTACION, ACTIVO
                        )
                        SELECT
                            'PRYGEN_' || TO_CHAR(P.ID_PROYECTO),
                            SUBSTR('Proyecto · ' || P.NOMBRE, 1, 250),
                            'Tarea técnica para imputación directa al proyecto.',
                            P.ID_PROYECTO, P.ID_UNIDAD_DUENA,
                            P.CLASIFICACION_COSTO, 'EN_EJECUCION', 'MEDIA',
                            P.FECHA_INICIO, P.FECHA_FIN, NULL,
                            P.PERMITE_IMPUTACION, P.ACTIVO
                        FROM GT_PROYECTO P
                        WHERE P.ID_PROYECTO = :id_proyecto
                        """,
                        {"id_proyecto": project_id},
                    )

            record_event("PROYECTOS", "GT_PROYECTO", "INSERT", project_id)
            flash("Proyecto creado correctamente.", "success")
            return redirect(url_for("projects.list_projects"))
        except Exception as exc:
            flash_exception(exc, context="Creación de proyecto")

    return render_template("projects/form.html", units=units, users=users)
