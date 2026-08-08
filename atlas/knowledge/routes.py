from __future__ import annotations

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

from ..errors import flash_exception
from ..security import login_required
from ..utils import parse_date
from .access import assert_document_access, can_edit_document, can_review_document
from .service import (
    CLASSIFICATIONS,
    DOCUMENT_TYPES,
    STATES,
    KnowledgePayload,
    catalogs,
    create_document,
    get_document,
    search_documents,
    transition_document,
    update_document,
)


bp = Blueprint("knowledge", __name__, url_prefix="/conocimiento")


@bp.before_request
def require_feature():
    if not current_app.config.get("KNOWLEDGE_ENABLED", False):
        abort(404)


def _optional_date(name: str, label: str):
    value = request.form.get(name, "").strip()
    return None if not value else parse_date(value, label)


def _payload() -> KnowledgePayload:
    reviewer = request.form.get("id_revisor", "").strip()
    return KnowledgePayload(
        tipo=request.form.get("tipo", ""),
        titulo=request.form.get("titulo", ""),
        resumen=request.form.get("resumen") or None,
        contenido=request.form.get("contenido") or None,
        etiquetas=request.form.get("etiquetas") or None,
        id_unidad=int(request.form["id_unidad"]),
        id_revisor=int(reviewer) if reviewer else None,
        clasificacion=request.form.get("clasificacion", "INTERNO"),
        fecha_vigencia=_optional_date("fecha_vigencia", "Fecha de vigencia"),
        fecha_prox_revision=_optional_date("fecha_prox_revision", "Próxima fecha de revisión"),
        motivo=request.form.get("motivo") or None,
    )


@bp.route("")
@login_required
def list_documents():
    try:
        documents = search_documents(
            query=request.args.get("q", ""),
            tipo=request.args.get("tipo", ""),
            estado=request.args.get("estado", ""),
        )
    except ValueError as exc:
        flash(str(exc), "error")
        documents = []
    return render_template(
        "knowledge/list.html",
        documents=documents,
        document_types=DOCUMENT_TYPES,
        states=STATES,
    )


@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def create():
    units, users = catalogs()
    if not units:
        flash("No tienes una unidad habilitada para crear documentación.", "error")
        return redirect(url_for("knowledge.list_documents"))

    if request.method == "POST":
        try:
            document_id = create_document(_payload())
            flash("Documento creado como borrador.", "success")
            return redirect(url_for("knowledge.detail", document_id=document_id))
        except Exception as exc:
            flash_exception(exc, context="Creación de conocimiento")

    return render_template(
        "knowledge/form.html",
        document=None,
        units=units,
        users=users,
        document_types=DOCUMENT_TYPES,
        classifications=CLASSIFICATIONS,
    )


@bp.route("/<int:document_id>")
@login_required
def detail(document_id: int):
    document = get_document(document_id)
    access_doc = assert_document_access(document_id)
    return render_template(
        "knowledge/detail.html",
        document=document,
        can_edit=can_edit_document(access_doc),
        can_review=can_review_document(access_doc),
    )


@bp.route("/<int:document_id>/editar", methods=["GET", "POST"])
@login_required
def edit(document_id: int):
    assert_document_access(document_id, edit=True)
    document = get_document(document_id)
    units, users = catalogs()

    if request.method == "POST":
        try:
            version = update_document(document_id, _payload())
            flash(f"Documento actualizado. Nueva versión: {version}.", "success")
            return redirect(url_for("knowledge.detail", document_id=document_id))
        except PermissionError:
            abort(403)
        except Exception as exc:
            flash_exception(exc, context="Edición de conocimiento")

    return render_template(
        "knowledge/form.html",
        document=document,
        units=units,
        users=users,
        document_types=DOCUMENT_TYPES,
        classifications=CLASSIFICATIONS,
    )


@bp.route("/<int:document_id>/estado", methods=["POST"])
@login_required
def change_state(document_id: int):
    try:
        transition_document(
            document_id,
            request.form.get("estado", ""),
            request.form.get("motivo") or None,
        )
        flash("Estado documental actualizado.", "success")
    except PermissionError:
        abort(403)
    except Exception as exc:
        flash_exception(exc, context="Flujo documental")
    return redirect(url_for("knowledge.detail", document_id=document_id))
