from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect

from .config import load_config

csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.update(load_config())
    if test_config:
        app.config.update(test_config)
    csrf.init_app(app)

    from .auth.routes import bp as auth_bp
    from .dashboard.routes import bp as dashboard_bp
    from .projects.routes import bp as projects_bp
    from .tasks.routes import bp as tasks_bp
    from .time_entries.routes import bp as time_entries_bp
    from .users.routes import bp as users_bp
    from .units.routes import bp as units_bp
    from .costs.routes import bp as costs_bp
    from .costs.access import can_manage_costs, can_view_costs

    for blueprint in (
        auth_bp, dashboard_bp, projects_bp, tasks_bp,
        time_entries_bp, users_bp, units_bp, costs_bp,
    ):
        app.register_blueprint(blueprint)

    @app.context_processor
    def inject_cost_access():
        return {
            "costs_visible": can_view_costs(),
            "costs_can_manage": can_manage_costs(),
        }

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        return render_template("errors/500.html"), 500

    return app
