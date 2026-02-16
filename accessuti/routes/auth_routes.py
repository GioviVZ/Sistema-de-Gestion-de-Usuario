from flask import Blueprint, render_template, request, redirect, url_for, flash, session

auth_bp = Blueprint("auth", __name__)

@auth_bp.get("/login")
def login():
    return render_template("login.html")

@auth_bp.post("/login")
def login_post():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    username = request.form.get("username","").strip().lower()
    password = request.form.get("password","")

    u = svc.validate_login(username, password)

    if not u:
        flash("Credenciales inválidas","danger")
        return redirect(url_for("auth.login"))

    session["user"] = {
        "username": u.username,
        "role": u.role
    }

    return redirect(url_for("users.dashboard"))

@auth_bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))