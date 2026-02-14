from functools import wraps
from flask import redirect, url_for, flash
from .auth import current_user

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            flash("Inicia sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)
    return wrapper

def role_required(*roles):
    roles = {r.upper() for r in roles}

    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            u = current_user()
            if not u:
                flash("Inicia sesión para continuar.", "warning")
                return redirect(url_for("auth.login"))
            if u.get("role", "").upper() not in roles:
                flash("No tienes permisos para acceder a esta sección.", "danger")
                return redirect(url_for("users.dashboard"))
            return fn(*args, **kwargs)
        return wrapper
    return deco