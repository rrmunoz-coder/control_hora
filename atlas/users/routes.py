from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from ..audit import record_event
from ..errors import flash_exception
from ..security import roles_required
from .security_service import revoke_sessions, reset_failed_attempts_secure
from .service import (
    create_ldap_user,
    get_catalogs,
    get_user,
    list_users as query_users,
    reset_failed_attempts,
    set_user_status,
    update_user,
)

bp = Blueprint(
    "users",
    __name__,
    url_prefix="/administracion/usuarios",
)


@bp.route("")
@roles_required("ADMIN")
def list_users():
    filters = {
        "q": request.args.get("q", "").strip(),
        "role": request.args.get("role", "").strip(),
        "status": request.args.get("status", "").strip(),
        "unit_id": request.args.get("unit_id", "").strip(),
    }

    users, summary = query_users(
        query=filters["q"],
        role=filters["role"],
        status=filters["status"],
        unit_id=filters["unit_id"],
    )
    catalogs = get_catalogs()

    return render_template(
        "users/list.html",
        users=users,
        summary=summary,
        roles=catalogs["roles"],
        units=catalogs["units"],
        filters=filters,
    )


@bp.route("/nuevo", methods=["GET", "POST"])
@roles_required("ADMIN")
def create_user():
    catalogs = get_catalogs()

    if request.method == "POST":
        try:
            user_id, after = create_ldap_user(request.form)
            record_event(
                "USUARIOS",
                "GT_USUARIO",
                "INSERT",
                user_id,
                after=after,
            )
            flash(
                "Usuario LDAP creado e inscrito correctamente.",
                "success",
            )
            return redirect(url_for("users.list_users"))
        except Exception as exc:
            flash_exception(exc, context="Gestión de usuarios")

    return render_template(
        "users/form.html",
        user=None,
        roles=catalogs["roles"],
        units=catalogs["units"],
        bosses=catalogs["bosses"],
        domain_suffix=current_app.config.get(
            "LDAP_DOMAIN_SUFFIX",
            "clarochile.org",
        ),
    )


@bp.route("/<int:user_id>/editar", methods=["GET", "POST"])
@roles_required("ADMIN")
def edit_user(user_id: int):
    user = get_user(user_id)
    if not user:
        abort(404)

    catalogs = get_catalogs(exclude_user_id=user_id)

    if request.method == "POST":
        try:
            before, after = update_user(user_id, request.form)
            revoke_sessions(user_id)
            record_event(
                "USUARIOS",
                "GT_USUARIO",
                "UPDATE",
                user_id,
                before=before,
                after=after,
            )
            flash("Usuario actualizado correctamente.", "success")
            return redirect(url_for("users.list_users"))
        except Exception as exc:
            flash_exception(exc, context="Gestión de usuarios")
            user = get_user(user_id) or user

    return render_template(
        "users/form.html",
        user=user,
        roles=catalogs["roles"],
        units=catalogs["units"],
        bosses=catalogs["bosses"],
        domain_suffix=current_app.config.get(
            "LDAP_DOMAIN_SUFFIX",
            "clarochile.org",
        ),
    )


@bp.route("/<int:user_id>/estado", methods=["POST"])
@roles_required("ADMIN")
def change_status(user_id: int):
    try:
        before, after = set_user_status(
            user_id,
            request.form.get("activo", "N"),
        )
        revoke_sessions(user_id)
        record_event(
            "USUARIOS",
            "GT_USUARIO",
            "STATUS",
            user_id,
            before=before,
            after=after,
        )
        message = (
            "Usuario activado correctamente."
            if after.get("activo") == "S"
            else "Usuario desactivado correctamente."
        )
        flash(message, "success")
    except Exception as exc:
        flash_exception(exc, context="Gestión de usuarios")

    return redirect(
        request.referrer or url_for("users.list_users")
    )


@bp.route("/<int:user_id>/reiniciar-intentos", methods=["POST"])
@roles_required("ADMIN")
def reset_attempts(user_id: int):
    try:
        before, _after = reset_failed_attempts(user_id)
        reset_failed_attempts_secure(user_id)
        after = get_user(user_id) or _after
        record_event(
            "USUARIOS",
            "GT_USUARIO_AUTH",
            "RESET_FAILED_ATTEMPTS",
            user_id,
            before=before,
            after=after,
        )
        flash(
            "Intentos fallidos reiniciados correctamente.",
            "success",
        )
    except Exception as exc:
        flash_exception(exc, context="Gestión de usuarios")

    return redirect(
        request.referrer or url_for("users.list_users")
    )
