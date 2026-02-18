from dataclasses import dataclass
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

from ..ds.bst import BST
from ..ds.linked_list import LinkedList
from ..ds.stack import Stack, audit_event


# =========================
# UTILIDADES
# =========================
def _parse_date(s: str):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except:
        return None


def _days_left(d):
    if not d:
        return None
    return (d - date.today()).days


def _as_bool(v) -> bool:
    return str(v or "").strip().lower() in ("1", "true", "on", "yes", "si")


# =========================
# MODELOS
# =========================
@dataclass
class AppUser:
    username: str
    password_hash: str
    role: str


@dataclass
class NetworkUser:
    usuario_red: str = ""
    nombres: str = ""
    apellidos: str = ""
    dni: str = ""
    tipo_contrato: str = ""
    contrato_inicio: str = ""
    contrato_fin: str = ""
    sede: str = ""
    dependencia: str = ""
    subdependencia: str = ""

    acceso_nivel: str = "NORMAL"
    acceso_redes_sociales: str = "NO"
    permiso_inicio: str = ""
    permiso_fin: str = ""

    vpn_activo: str = "NO"
    vpn_inicio: str = ""
    vpn_fin: str = ""

    permisos_activos: str = "SI"
    status: str = "ACTIVE"


# =========================
# SERVICIO PRINCIPAL
# =========================
class UserService:
    def __init__(self, store):
        self.store = store
        self.audit = Stack()
        self._bst = BST()
        self._list = LinkedList()

        self._load_network_users()

        # Usuarios fijos del sistema
        self.app_users = {
            "admin": AppUser("admin", generate_password_hash("admin123"), "ADMIN"),
            "consulta": AppUser("consulta", generate_password_hash("consulta123"), "CONSULTA"),
        }

    # ================= LOGIN =================
    def validate_login(self, username, password):
        username = (username or "").strip().lower()
        u = self.app_users.get(username)
        if not u:
            return None
        if not check_password_hash(u.password_hash, password):
            return None
        return u

    # ================= LOAD =================
    def _load_network_users(self):
        self._bst = BST()
        self._list = LinkedList()

        for r in self.store.read_all():
            u = NetworkUser(**r)

            if not u.usuario_red:
                continue

            key = u.usuario_red.strip().lower()
            u.usuario_red = key

            self._bst.insert(key, u)
            self._list.append(u)

    # ================= MÉTRICAS =================
    def bst_metrics(self):
        return {"comparisons": getattr(self._bst, "last_comparisons", 0)}

    # ================= HELPERS =================
    def _upsert_row(self, usuario_red: str, new_row: dict):
        rows = self.store.read_all()
        found = False

        for row in rows:
            if (row.get("usuario_red") or "").strip().lower() == usuario_red:
                row.update(new_row)
                found = True
                break

        if not found:
            rows.append(new_row)

        self.store.write_all(rows)
        self._load_network_users()

    def _active_users(self):
        return [u for u in self._list.to_list() if u.status == "ACTIVE"]

    # ================= CRUD =================
    def register_network_user(self, data: dict, actor="admin"):
        usuario_red = (data.get("usuario_red") or "").strip().lower()
        if not usuario_red:
            raise ValueError("usuario_red es obligatorio.")

        def norm(v): return (v or "").strip()

        new_row = {
            "usuario_red": usuario_red,
            "nombres": norm(data.get("nombres")),
            "apellidos": norm(data.get("apellidos")),
            "dni": norm(data.get("dni")),
            "tipo_contrato": norm(data.get("tipo_contrato")).upper(),
            "contrato_inicio": norm(data.get("contrato_inicio")),
            "contrato_fin": norm(data.get("contrato_fin")),
            "sede": norm(data.get("sede")),
            "dependencia": norm(data.get("dependencia")),
            "subdependencia": norm(data.get("subdependencia")),

            "acceso_nivel": (norm(data.get("acceso_nivel")) or "NORMAL").upper(),
            "acceso_redes_sociales": (norm(data.get("acceso_redes_sociales")) or "NO").upper(),
            "permiso_inicio": norm(data.get("permiso_inicio")),
            "permiso_fin": norm(data.get("permiso_fin")),

            "vpn_activo": (norm(data.get("vpn_activo")) or "NO").upper(),
            "vpn_inicio": norm(data.get("vpn_inicio")),
            "vpn_fin": norm(data.get("vpn_fin")),

            "permisos_activos": (norm(data.get("permisos_activos")) or "SI").upper(),
            "status": "ACTIVE",
        }

        self._upsert_row(usuario_red, new_row)
        self.audit.push(audit_event(f"Registrado/actualizado {usuario_red}", actor))

    def deactivate_user(self, usuario_red, actor="admin"):
        usuario_red = (usuario_red or "").strip().lower()
        rows = self.store.read_all()
        ok = False

        for row in rows:
            if (row.get("usuario_red") or "").strip().lower() == usuario_red:
                row["status"] = "INACTIVE"
                ok = True
                break

        if not ok:
            raise ValueError("Usuario no existe.")

        self.store.write_all(rows)
        self._load_network_users()
        self.audit.push(audit_event(f"Desactivado usuario {usuario_red}", actor))

    def activate_user(self, usuario_red, actor="admin"):
        usuario_red = (usuario_red or "").strip().lower()
        rows = self.store.read_all()
        ok = False

        for row in rows:
            if (row.get("usuario_red") or "").strip().lower() == usuario_red:
                row["status"] = "ACTIVE"
                ok = True
                break

        if not ok:
            raise ValueError("Usuario no existe.")

        self.store.write_all(rows)
        self._load_network_users()
        self.audit.push(audit_event(f"Reactivado usuario {usuario_red}", actor))

    def deactivate_special_permissions(self, usuario_red, actor="admin"):
        usuario_red = (usuario_red or "").strip().lower()
        rows = self.store.read_all()
        ok = False

        for row in rows:
            if (row.get("usuario_red") or "").strip().lower() == usuario_red:
                row["permisos_activos"] = "NO"
                row["vpn_activo"] = "NO"
                row["acceso_redes_sociales"] = "NO"
                ok = True
                break

        if not ok:
            raise ValueError("Usuario no existe.")

        self.store.write_all(rows)
        self._load_network_users()
        self.audit.push(audit_event(f"Permisos especiales apagados {usuario_red}", actor))

    # ================= QUERIES =================
    def get_network_user(self, usuario_red):
        return self._bst.search((usuario_red or "").strip().lower())

    def total_network_users(self):
        return sum(1 for u in self._list.to_list() if u.status == "ACTIVE")

    # ================= FILTROS (CONSULTA) =================
    def filter_users(
        self,
        nombre=None,
        sede=None,
        dependencia=None,
        subdependencia=None,
        permisos_activos=None,
        vpn_activo=None,
        acceso_redes_sociales=None,
        acceso_nivel=None,
        estado=None,               # "ACTIVE" | "INACTIVE" | ""
        include_inactive=False,    # mezcla
    ):
        results = []

        nombre = (nombre or "").strip().lower()
        sede = (sede or "").strip()
        dependencia = (dependencia or "").strip()
        subdependencia = (subdependencia or "").strip()

        permisos_activos = (permisos_activos or "").strip().upper()  # SI/NO
        vpn_activo = (vpn_activo or "").strip().upper()              # SI/NO
        acceso_redes_sociales = (acceso_redes_sociales or "").strip().upper()  # SI/NO
        acceso_nivel = (acceso_nivel or "").strip().upper()          # NORMAL/ADMINISTRADOR

        estado = (estado or "").strip().upper()
        include_inactive = _as_bool(include_inactive)

        for u in self._list.to_list():
            # estado explícito manda
            if estado == "ACTIVE" and u.status != "ACTIVE":
                continue
            if estado == "INACTIVE" and u.status != "INACTIVE":
                continue

            # por defecto, solo activos (si no se pidió estado específico)
            if not estado and not include_inactive and u.status != "ACTIVE":
                continue

            if nombre:
                full = f"{u.nombres} {u.apellidos}".lower()
                if nombre not in full and nombre not in (u.usuario_red or ""):
                    continue

            if sede and u.sede != sede:
                continue
            if dependencia and u.dependencia != dependencia:
                continue
            if subdependencia and u.subdependencia != subdependencia:
                continue

            if permisos_activos in ("SI", "NO") and (u.permisos_activos or "").upper() != permisos_activos:
                continue
            if vpn_activo in ("SI", "NO") and (u.vpn_activo or "").upper() != vpn_activo:
                continue
            if acceso_redes_sociales in ("SI", "NO") and (u.acceso_redes_sociales or "").upper() != acceso_redes_sociales:
                continue
            if acceso_nivel and (u.acceso_nivel or "").upper() != acceso_nivel:
                continue

            results.append(u)

        return results

    # ================= ALERTAS =================
    def expiring_alerts(self, days=15):
        alerts = []
        for u in self._active_users():
            cfin = _parse_date(u.contrato_fin)
            left = _days_left(cfin)
            if left is not None and left <= days:
                alerts.append({"tipo": "CONTRATO", "u": u, "dias": left, "vence": u.contrato_fin})

            if (u.permisos_activos or "").upper() == "SI":
                pfin = _parse_date(u.permiso_fin)
                leftp = _days_left(pfin)
                if leftp is not None and leftp <= days:
                    alerts.append({"tipo": "PERMISOS", "u": u, "dias": leftp, "vence": u.permiso_fin})

            if (u.vpn_activo or "").upper() == "SI":
                vfin = _parse_date(u.vpn_fin)
                leftv = _days_left(vfin)
                if leftv is not None and leftv <= days:
                    alerts.append({"tipo": "VPN", "u": u, "dias": leftv, "vence": u.vpn_fin})

        alerts.sort(key=lambda x: x["dias"])
        return alerts

    # ================= DASHBOARD COUNTS (activos) =================
    def count_by_sede(self):
        counts = {}
        for u in self._active_users():
            sede = (u.sede or "SIN SEDE").strip() or "SIN SEDE"
            counts[sede] = counts.get(sede, 0) + 1
        return counts

    def count_by_dependencia(self):
        counts = {}
        for u in self._active_users():
            dep = (u.dependencia or "SIN DEPENDENCIA").strip() or "SIN DEPENDENCIA"
            counts[dep] = counts.get(dep, 0) + 1
        return counts

    def count_by_subdependencia(self):
        counts = {}
        for u in self._active_users():
            sub = (u.subdependencia or "SIN SUBDEPENDENCIA").strip() or "SIN SUBDEPENDENCIA"
            counts[sub] = counts.get(sub, 0) + 1
        return counts

    def count_by_contrato(self):
        counts = {}
        for u in self._active_users():
            tipo = (u.tipo_contrato or "SIN TIPO").strip().upper() or "SIN TIPO"
            counts[tipo] = counts.get(tipo, 0) + 1
        return counts

    def count_vpn_activo(self):
        counts = {"SI": 0, "NO": 0}
        for u in self._active_users():
            v = (u.vpn_activo or "NO").strip().upper()
            counts["SI" if v == "SI" else "NO"] += 1
        return counts

    def count_permisos_activos(self):
        counts = {"SI": 0, "NO": 0}
        for u in self._active_users():
            p = (u.permisos_activos or "NO").strip().upper()
            counts["SI" if p == "SI" else "NO"] += 1
        return counts

    def count_acceso_redes_sociales(self):
        counts = {"SI": 0, "NO": 0}
        for u in self._active_users():
            r = (u.acceso_redes_sociales or "NO").strip().upper()
            counts["SI" if r == "SI" else "NO"] += 1
        return counts

    def count_acceso_nivel(self):
        counts = {}
        for u in self._active_users():
            lvl = (u.acceso_nivel or "NORMAL").strip().upper() or "NORMAL"
            counts[lvl] = counts.get(lvl, 0) + 1
        return counts