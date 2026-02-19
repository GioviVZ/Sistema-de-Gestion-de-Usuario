import csv
import os
from datetime import datetime
from typing import Dict, List, Optional

DEFAULT_FIELDS = [
    "usuario_red", "dni", "nombres", "apellidos",
    "correo", "ip_equipo", "host",

    "tipo_contrato", "contrato_inicio", "contrato_fin",
    "sede", "dependencia", "subdependencia",

    "equipo_personal",
    "antivirus", "antivirus_fin",

    "acceso_nivel", "acceso_redes_sociales",
    "permisos_activos", "permiso_inicio", "permiso_fin",
    "vpn_activo", "vpn_inicio", "vpn_fin",
    "status"
]

class CSVStore:
    def __init__(self, base_dir: str, audit=None):
        # base_dir debe ser una carpeta: accessuti/data
        self.base_dir = base_dir
        self.data_dir = base_dir
        self.backups_dir = os.path.join(base_dir, "backups")
        self.exports_dir = os.path.join(base_dir, "exports")
        self.logs_dir = os.path.join(base_dir, "logs")

        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backups_dir, exist_ok=True)
        os.makedirs(self.exports_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

        self.users_path = os.path.join(self.data_dir, "users.csv")
        self.audit = audit

    # ========= lo que tu UserService espera =========
    def read_all(self) -> List[Dict]:
        return self._read_all()

    def write_all(self, rows: List[Dict], fields: List[str] = None):
        return self._write_all(rows, fields=fields)

    # ================= internos =================
    def _ensure_file(self, fields: List[str] = None):
        fields = fields or DEFAULT_FIELDS

        # crear si no existe
        if not os.path.exists(self.users_path):
            with open(self.users_path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
            if self.audit:
                self.audit.log("FILE_CREATE", meta={"path": self.users_path})
            return

        # si existe, migrar headers/campos
        self.migrate_schema()

    def migrate_schema(self):
        """Asegura que users.csv tenga todas las columnas de DEFAULT_FIELDS sin perder data."""
        if not os.path.exists(self.users_path):
            return

        # leer con headers actuales
        with open(self.users_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            current_fields = reader.fieldnames or []
            rows = [dict(r) for r in reader]

        # si ya coincide, no hacer nada
        if list(current_fields) == list(DEFAULT_FIELDS):
            return

        # reescribir con DEFAULT_FIELDS rellenando faltantes con ""
        with open(self.users_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=DEFAULT_FIELDS)
            w.writeheader()
            for row in rows:
                clean = {k: (row.get(k, "") if row.get(k, "") is not None else "") for k in DEFAULT_FIELDS}
                w.writerow(clean)

        if self.audit:
            self.audit.log("SCHEMA_MIGRATE", meta={"path": self.users_path, "from": current_fields})

    def _read_all(self) -> List[Dict]:
        self._ensure_file()
        with open(self.users_path, "r", newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            return [dict(row) for row in r]

    def _write_all(self, rows: List[Dict], fields: List[str] = None):
        fields = fields or DEFAULT_FIELDS
        self._ensure_file(fields=fields)
        with open(self.users_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for row in rows:
                clean = {k: (row.get(k, "") if row.get(k, "") is not None else "") for k in fields}
                w.writerow(clean)

    def backup(self) -> str:
        self._ensure_file()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = os.path.join(self.backups_dir, f"users_{ts}.csv")
        with open(self.users_path, "rb") as src_f, open(dst, "wb") as dst_f:
            dst_f.write(src_f.read())
        if self.audit:
            self.audit.log("BACKUP_CREATE", meta={"dst": dst})
        return dst

    def upsert_user(self, user: Dict, actor: str = "unknown", ip: str = "-") -> Dict:
        self._ensure_file()
        rows = self._read_all()

        key = (user.get("usuario_red") or "").strip().lower()
        if not key:
            raise ValueError("usuario_red es obligatorio")

        self.backup()

        updated = False
        before = None
        for i, r in enumerate(rows):
            if (r.get("usuario_red") or "").strip().lower() == key:
                before = dict(r)
                rows[i] = {**r, **user, "usuario_red": key}
                updated = True
                break

        if not updated:
            rows.append({**user, "usuario_red": key})

        self._write_all(rows, fields=DEFAULT_FIELDS)

        if self.audit:
            self.audit.log(
                "USER_UPDATE" if updated else "USER_CREATE",
                actor=actor,
                ip=ip,
                meta={"usuario_red": key, "before": before if updated else None}
            )

        return {"ok": True, "updated": updated, "usuario_red": key}

    def export_csv(self, filename_prefix: str = "export_users", rows: Optional[List[Dict]] = None,
                   actor: str = "unknown", ip: str = "-") -> str:
        self._ensure_file()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = os.path.join(self.exports_dir, f"{filename_prefix}_{ts}.csv")

        data = rows if rows is not None else self._read_all()

        with open(export_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=DEFAULT_FIELDS)
            w.writeheader()
            for row in data:
                clean = {k: (row.get(k, "") if row.get(k, "") is not None else "") for k in DEFAULT_FIELDS}
                w.writerow(clean)

        if self.audit:
            self.audit.log("EXPORT_CSV", actor=actor, ip=ip, meta={"path": export_path, "count": len(data)})

        return export_path