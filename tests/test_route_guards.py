from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ROOT / "atlas"
PUBLIC_FUNCTIONS = {("auth/routes.py", "login"), ("auth/routes.py", "logout")}
AUTH_GUARDS = {"login_required", "roles_required", "costs_view_required", "costs_manage_required"}


def _decorator_name(node):
    if isinstance(node, ast.Call):
        node = node.func
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def test_every_non_public_route_has_server_side_guard():
    unguarded = []
    for path in ROUTES.rglob("routes.py"):
        rel = str(path.relative_to(ROUTES)).replace("\\", "/")
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            decorators = {_decorator_name(item) for item in node.decorator_list}
            is_route = "route" in decorators
            if not is_route or (rel, node.name) in PUBLIC_FUNCTIONS:
                continue
            if not (decorators & AUTH_GUARDS):
                unguarded.append(f"{rel}:{node.name}")
    assert not unguarded, f"Rutas sin guardia: {unguarded}"
