from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..core.auth import login_user, logout_user
from ..core.decorators import login_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.get("/login")
def login():
    return render_template("login.html")

@auth_bp.post("/login")
def login_post():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    u = svc.validate_login(username, password)
    if not u:
        flash("Credenciales inválidas o usuario inactivo.", "danger")
        return redirect(url_for("auth.login"))

    login_user({"username": u.username, "full_name": u.full_name, "role": u.role})
    flash(f"Bienvenido, {u.full_name or u.username}.", "success")
    return redirect(url_for("users.dashboard"))

@auth_bp.get("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))