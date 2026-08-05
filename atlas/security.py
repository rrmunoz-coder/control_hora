from functools import wraps

from flask import abort, redirect, session, url_for


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("id_usuario"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def roles_required(*roles):
    allowed = {role.upper() for role in roles}

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("id_usuario"):
                return redirect(url_for("auth.login"))
            if str(session.get("rol_codigo", "")).upper() not in allowed:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator
