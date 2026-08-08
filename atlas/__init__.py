from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import uuid

from flask import Flask, g, redirect, render_template, request
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import load_config
from .errors import request_id
from .security import enforce_session

csrf = CSRFProtect()


def _configure_logging(app: Flask) -> None:
    if app.testing:
        return
    log_dir = Path(app.root_path).parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        log_dir / "atlas.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
    )
    handler.setLevel(logging.INFO)
    root_logger = logging.getLogger()
    if not any(isinstance(item, RotatingFileHandler) for item in root_logger.handlers):
        root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.update(load_config())
    if test_config:
        app.config.update(test_config)

    app.config.setdefault("SESSION_REFRESH_EACH_REQUEST", False)
    app.config["MAX_CONTENT_LENGTH"] = (
        app.config.get("MAX_CONTENT_LENGTH") or 10 * 1024 * 1024
    )
    if app.config.get("KNOWLEDGE_ENABLED"):
        app.config["MAX_CONTENT_LENGTH"] = max(
            int(app.config["MAX_CONTENT_LENGTH"]),
            int(app.config.get("KNOWLEDGE_MAX_FILE_MB", 25)) * 1024 * 1024,
        )

    if app.config.get("TRUST_PROXY_HEADERS"):
        hops = int(app.config.get("TRUSTED_PROXY_HOPS", 1))
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=hops,
            x_proto=hops,
            x_host=hops,
            x_port=hops,
        )

    _configure_logging(app)
    csrf.init_app(app)

    from .auth.routes import bp as auth_bp
    from .dashboard.routes import bp as dashboard_bp
    from .projects.routes import bp as projects_bp
    from .tasks.routes import bp as tasks_bp
    from .time_entries.routes import bp as time_entries_bp
    from .approvals.routes import bp as approvals_bp
    from .users.routes import bp as users_bp
    from .units.routes import bp as units_bp
    from .costs.routes import bp as costs_bp
    from .costs.access import can_manage_costs, can_view_costs

    blueprints = [
        auth_bp, dashboard_bp, projects_bp, tasks_bp,
        time_entries_bp, approvals_bp, users_bp, units_bp, costs_bp,
    ]
    if app.config.get("KNOWLEDGE_ENABLED"):
        from .knowledge.routes import bp as knowledge_bp
        blueprints.append(knowledge_bp)

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    @app.before_request
    def protect_request():
        supplied = ""
        if app.config.get("TRUST_PROXY_HEADERS"):
            supplied = request.headers.get("X-Request-ID", "").strip()
        g.request_id = (
            supplied[:64]
            if supplied and supplied.isascii()
            else uuid.uuid4().hex[:12]
        )

        if app.config.get("FORCE_HTTPS") and not request.is_secure:
            secure_url = request.url.replace("http://", "https://", 1)
            return redirect(secure_url, code=307)

        if request.endpoint == "static":
            return None
        return enforce_session()

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = app.config["CONTENT_SECURITY_POLICY"]
        response.headers["X-Request-ID"] = request_id()
        if request.is_secure:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={int(app.config['HSTS_SECONDS'])}; includeSubDomains"
            )
        if request.endpoint and request.endpoint != "static":
            response.headers.setdefault("Cache-Control", "no-store")
        return response

    @app.context_processor
    def inject_access():
        return {
            "costs_visible": can_view_costs(),
            "costs_can_manage": can_manage_costs(),
            "knowledge_enabled": bool(app.config.get("KNOWLEDGE_ENABLED")),
        }

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        app.logger.warning("CSRF rechazado: %s [incidente=%s]", error.description, request_id())
        return render_template(
            "errors/400.html",
            message="La sesión del formulario expiró o el formulario no es válido.",
            request_id=request_id(),
        ), 400

    @app.errorhandler(403)
    def forbidden(error):
        app.logger.warning("Acceso denegado: %s [incidente=%s]", error, request_id())
        return render_template("errors/403.html", request_id=request_id()), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html", request_id=request_id()), 404

    @app.errorhandler(500)
    def server_error(error):
        app.logger.error(
            "Error no controlado [incidente=%s]",
            request_id(),
            exc_info=(type(error), error, error.__traceback__),
        )
        return render_template("errors/500.html", request_id=request_id()), 500

    return app
