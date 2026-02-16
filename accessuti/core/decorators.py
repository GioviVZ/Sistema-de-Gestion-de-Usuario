from functools import wraps
from flask import redirect, url_for, flash
from .auth import current_user

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            flash("Inicia sesión.", "warning")
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)
    return wrapper

def role_required(role):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            u = current_user()
            if not u or u.get("role") != role:
                flash("No tienes permisos.", "danger")
                return redirect(url_for("users.dashboard"))
            return fn(*args, **kwargs)
        return wrapper
    return deco