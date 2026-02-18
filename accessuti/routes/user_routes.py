from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from ..core.decorators import login_required
from ..core.auth import current_user
from time import time

users_bp = Blueprint("users", __name__)

# ---------------- helpers ----------------
def _dict_to_xy(d: dict):
    return [{"category": k, "value": v} for k, v in (d or {}).items()]

def _top_n_with_others(d: dict, n=10, other_label="OTROS"):
    items = sorted((d or {}).items(), key=lambda kv: kv[1], reverse=True)
    top = items[:n]
    rest = items[n:]
    out = dict(top)
    if rest:
        out[other_label] = sum(v for _, v in rest)
    return out


# =========================
# DASHBOARD + CONSULTA
# =========================
@users_bp.get("/")
@login_required
def dashboard():
    from flask import current_app
    svc = current_app.extensions["user_service"]
    user = current_user()

    # filtros consulta
    nombre = request.args.get("nombre", "").strip()
    sede = request.args.get("sede", "").strip()
    dependencia = request.args.get("dependencia", "").strip()
    subdependencia = request.args.get("subdependencia", "").strip()

    # filtros “permisos especiales”
    permisos_activos = request.args.get("permisos_activos", "").strip().upper()
    vpn_activo = request.args.get("vpn_activo", "").strip().upper()
    acceso_redes_sociales = request.args.get("acceso_redes_sociales", "").strip().upper()
    acceso_nivel = request.args.get("acceso_nivel", "").strip().upper()

    # estado / include_inactive (tal como tu HTML)
    estado = request.args.get("estado", "").strip().upper()  # ACTIVE/INACTIVE/""
    include_inactive = request.args.get("include_inactive", "")  # "on" si marcado

    filtered = svc.filter_users(
        nombre=nombre,
        sede=sede,
        dependencia=dependencia,
        subdependencia=subdependencia,
        permisos_activos=permisos_activos,
        vpn_activo=vpn_activo,
        acceso_redes_sociales=acceso_redes_sociales,
        acceso_nivel=acceso_nivel,
        estado=estado,
        include_inactive=include_inactive,
    )

    return render_template(
        "dashboard.html",
        user=user,

        total=svc.total_network_users(),
        total_filtrados=len(filtered),
        alerts=svc.expiring_alerts(15),
        metrics=svc.bst_metrics(),
        filtered=filtered,

        # persistencia filtros
        nombre=nombre,
        sede=sede,
        dependencia=dependencia,
        subdependencia=subdependencia,
        permisos_activos=permisos_activos,
        vpn_activo=vpn_activo,
        acceso_redes_sociales=acceso_redes_sociales,
        acceso_nivel=acceso_nivel,
        estado=estado,
        include_inactive=include_inactive,

        now_ts=int(time()),  # cache-bust para assets/requests si lo necesitas
    )


# =========================
# REGISTRO / UPDATE (solo ADMIN)
# =========================
@users_bp.post("/register")
@login_required
def register_network_user():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    u = current_user()
    if u.get("role") != "ADMIN":
        flash("No tienes permisos para registrar/editar usuarios.", "danger")
        return redirect(url_for("users.dashboard"))

    actor = u.get("username", "admin")

    try:
        svc.register_network_user(dict(request.form), actor=actor)
        flash("Usuario registrado/actualizado correctamente.", "success")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("users.dashboard"))


@users_bp.post("/user/deactivate")
@login_required
def user_deactivate():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    u = current_user()
    if u.get("role") != "ADMIN":
        flash("No tienes permisos.", "danger")
        return redirect(url_for("users.dashboard"))

    actor = u.get("username", "admin")
    usuario_red = request.form.get("usuario_red", "")

    try:
        svc.deactivate_user(usuario_red, actor=actor)
        flash("Usuario desactivado.", "info")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("users.dashboard"))


@users_bp.post("/user/activate")
@login_required
def user_activate():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    u = current_user()
    if u.get("role") != "ADMIN":
        flash("No tienes permisos.", "danger")
        return redirect(url_for("users.dashboard"))

    actor = u.get("username", "admin")
    usuario_red = request.form.get("usuario_red", "")

    try:
        svc.activate_user(usuario_red, actor=actor)
        flash("Usuario reactivado.", "success")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("users.dashboard"))


@users_bp.post("/user/perms_off")
@login_required
def user_perms_off():
    from flask import current_app
    svc = current_app.extensions["user_service"]

    u = current_user()
    if u.get("role") != "ADMIN":
        flash("No tienes permisos.", "danger")
        return redirect(url_for("users.dashboard"))

    actor = u.get("username", "admin")
    usuario_red = request.form.get("usuario_red", "")

    try:
        svc.deactivate_special_permissions(usuario_red, actor=actor)
        flash("Permisos especiales apagados.", "info")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("users.dashboard"))


# =========================
# API CHARTS (JSON)
# =========================
@users_bp.get("/api/charts/sede")
@login_required
def api_chart_sede():
    from flask import current_app
    svc = current_app.extensions["user_service"]
    return jsonify(_dict_to_xy(svc.count_by_sede()))

@users_bp.get("/api/charts/contrato")
@login_required
def api_chart_contrato():
    from flask import current_app
    svc = current_app.extensions["user_service"]
    return jsonify(_dict_to_xy(svc.count_by_contrato()))

@users_bp.get("/api/charts/dependencia")
@login_required
def api_chart_dependencia():
    from flask import current_app
    svc = current_app.extensions["user_service"]
    d = _top_n_with_others(svc.count_by_dependencia(), n=10, other_label="OTROS")
    return jsonify(_dict_to_xy(d))

@users_bp.get("/api/charts/subdependencia")
@login_required
def api_chart_subdependencia():
    from flask import current_app
    svc = current_app.extensions["user_service"]
    d = _top_n_with_others(svc.count_by_subdependencia(), n=10, other_label="OTROS")
    return jsonify(_dict_to_xy(d))

@users_bp.get("/api/charts/permisos")
@login_required
def api_chart_permisos():
    from flask import current_app
    svc = current_app.extensions["user_service"]
    return jsonify(_dict_to_xy(svc.count_permisos_activos()))

@users_bp.get("/api/charts/vpn")
@login_required
def api_chart_vpn():
    from flask import current_app
    svc = current_app.extensions["user_service"]
    return jsonify(_dict_to_xy(svc.count_vpn_activo()))

@users_bp.get("/api/charts/redes")
@login_required
def api_chart_redes():
    from flask import current_app
    svc = current_app.extensions["user_service"]
    return jsonify(_dict_to_xy(svc.count_acceso_redes_sociales()))

@users_bp.get("/api/charts/nivel")
@login_required
def api_chart_nivel():
    from flask import current_app
    svc = current_app.extensions["user_service"]
    return jsonify(_dict_to_xy(svc.count_acceso_nivel()))