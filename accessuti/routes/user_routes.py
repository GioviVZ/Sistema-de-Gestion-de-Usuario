from flask import Blueprint, render_template
from ..core.decorators import login_required, role_required
from ..core.auth import current_user

users_bp = Blueprint("users", __name__)

@users_bp.get("/")
@login_required
def dashboard():
    from flask import current_app
    svc = current_app.extensions["user_service"]
    u = current_user()

    total = len(svc.list_users())
    audit = svc.audit_tail(10)

    return render_template("dashboard.html", user=u, total_users=total, audit=audit)

@users_bp.get("/users")
@login_required
@role_required("ADMIN")
def users_list():
    from flask import current_app
    svc = current_app.extensions["user_service"]
    users = svc.list_users()
    return render_template("users.html", users=users, user=current_user())