import csv, os

FIELDS = [
    "usuario_red",
    "nombres",
    "apellidos",
    "dni",
    "tipo_contrato",
    "contrato_inicio",
    "contrato_fin",
    "sede",
    "dependencia",
    "subdependencia",

    # Permisos especiales
    "acceso_nivel",            # LIBRE | COMUN | NORMAL
    "acceso_redes_sociales",   # SI | NO
    "permiso_inicio",
    "permiso_fin",

    # VPN
    "vpn_activo",              # SI | NO
    "vpn_inicio",
    "vpn_fin",

    # Estados
    "permisos_activos",        # SI | NO
    "status"                   # ACTIVE | INACTIVE
]

class CSVStore:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if not os.path.exists(path):
            with open(path, "w", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=FIELDS).writeheader()

    def read_all(self):
        if not os.path.exists(self.path):
            with open(self.path, "w", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=FIELDS).writeheader()

        with open(self.path, "r", newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            out = []
            for row in r:
                # compatibilidad: rellenar faltantes
                fixed = {k: (row.get(k, "") or "") for k in FIELDS}
                # si venía "username" viejo, úsalo como usuario_red si falta
                if not fixed["usuario_red"] and row.get("username"):
                    fixed["usuario_red"] = (row.get("username") or "").strip().lower()
                out.append(fixed)
            return out

    def write_all(self, rows):
        with open(self.path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            for row in rows:
                w.writerow({k: row.get(k, "") for k in FIELDS})