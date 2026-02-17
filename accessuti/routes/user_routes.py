from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from ..core.decorators import login_required
from ..core.auth import current_user

import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

users_bp = Blueprint("users", __name__)

# =========================
# DASHBOARD
# =========================
@users_bp.get("/")
@login_required
def dashboard():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    q = request.args.get("q", "").strip()
    nombre = request.args.get("nombre", "").strip()
    sede = request.args.get("sede", "").strip()
    dependencia = request.args.get("dependencia", "").strip()
    subdependencia = request.args.get("subdependencia", "").strip()

    result = svc.get_network_user(q) if q else None

    filtered = svc.filter_users(
        nombre=nombre,
        sede=sede,
        dependencia=dependencia,
        subdependencia=subdependencia
    )

    return render_template(
        "dashboard.html",
        user=current_user(),
        q=q,
        result=result,
        total=svc.total_network_users(),
        alerts=svc.expiring_alerts(15),
        audit=svc.audit.to_list()[:10],
        metrics=svc.bst_metrics(),
        filtered=filtered,
        nombre=nombre,
        sede=sede,
        dependencia=dependencia,
        subdependencia=subdependencia
    )
from time import time

def dashboard():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    q = request.args.get("q", "").strip()
    nombre = request.args.get("nombre", "").strip()
    sede = request.args.get("sede", "").strip()
    dependencia = request.args.get("dependencia", "").strip()
    subdependencia = request.args.get("subdependencia", "").strip()

    result = svc.get_network_user(q) if q else None

    filtered = svc.filter_users(
        nombre=nombre,
        sede=sede,
        dependencia=dependencia,
        subdependencia=subdependencia
    )

    return render_template(
        "dashboard.html",
        user=current_user(),
        q=q,
        result=result,
        total=svc.total_network_users(),
        alerts=svc.expiring_alerts(15),
        audit=svc.audit.to_list()[:10],
        metrics=svc.bst_metrics(),
        filtered=filtered,
        nombre=nombre,
        sede=sede,
        dependencia=dependencia,
        subdependencia=subdependencia,
        now_ts=int(time())   # ✅ cache bust
    )
@users_bp.get("/chart/alerts")
@login_required
def chart_alerts_by_tipo():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    data = svc.count_alerts_by_tipo(15)
    if not data:
        data = {"Sin alertas": 1}

    labels = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(labels, values)
    ax.set_title("Alertas por tipo (próximos 15 días)")
    ax.set_ylabel("Cantidad")
    ax.set_xlabel("Tipo")
    plt.xticks(rotation=0)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)

    return Response(img.getvalue(), mimetype="image/png")
# =========================
# REGISTRO / UPDATE
# =========================
@users_bp.post("/register")
@login_required
def register_network_user():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    actor = current_user().get("username", "admin")

    try:
        svc.register_network_user(dict(request.form), actor=actor)
        flash("Usuario registrado/actualizado correctamente.", "success")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("users.dashboard"))

# =========================
# DESACTIVAR
# =========================
@users_bp.post("/user/deactivate")
@login_required
def user_deactivate():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    user = current_user()
    if user.get("role") != "ADMIN":
        flash("No tienes permisos.", "danger")
        return redirect(url_for("users.dashboard"))

    actor = user.get("username", "admin")
    usuario_red = request.form.get("usuario_red", "")

    try:
        svc.deactivate_user(usuario_red, actor=actor)
        flash("Usuario desactivado.", "info")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("users.dashboard"))

# =========================
# REACTIVAR
# =========================
@users_bp.post("/user/activate")
@login_required
def user_activate():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    user = current_user()
    if user.get("role") != "ADMIN":
        flash("No tienes permisos.", "danger")
        return redirect(url_for("users.dashboard"))

    actor = user.get("username", "admin")
    usuario_red = request.form.get("usuario_red", "")

    try:
        svc.activate_user(usuario_red, actor=actor)
        flash("Usuario reactivado.", "success")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("users.dashboard"))

# =========================
# APAGAR PERMISOS
# =========================
@users_bp.post("/user/perms_off")
@login_required
def user_perms_off():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    user = current_user()
    if user.get("role") != "ADMIN":
        flash("No tienes permisos.", "danger")
        return redirect(url_for("users.dashboard"))

    actor = user.get("username", "admin")
    usuario_red = request.form.get("usuario_red", "")

    try:
        svc.deactivate_special_permissions(usuario_red, actor=actor)
        flash("Permisos especiales apagados.", "info")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("users.dashboard"))

# =========================
# CHART: SEDE
# =========================
@users_bp.get("/chart/sede")
@login_required
def chart_users_by_sede():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    data = svc.count_by_sede()

    if not data:
        data = {"Sin datos": 1}

    labels = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(labels, values)
    ax.set_title("Usuarios activos por sede")
    ax.set_ylabel("Cantidad")
    ax.set_xlabel("Sede")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)

    return Response(img.getvalue(), mimetype="image/png")

# =========================
# CHART: TIPO CONTRATO
# =========================
@users_bp.get("/chart/contrato")
@login_required
def chart_users_by_contrato():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    data = svc.count_by_contrato()

    if not data:
        data = {"Sin datos": 1}

    labels = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(labels, values)
    ax.set_title("Usuarios activos por tipo de contrato")
    ax.set_ylabel("Cantidad")
    ax.set_xlabel("Tipo")
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)

    return Response(img.getvalue(), mimetype="image/png")