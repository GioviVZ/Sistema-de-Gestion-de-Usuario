from dataclasses import dataclass
from typing import Optional, List
from werkzeug.security import generate_password_hash, check_password_hash

from ..ds.bst import BST
from ..ds.linked_list import LinkedList
from ..ds.stack import Stack
from ..storage.csv_store import CSVStore


@dataclass
class User:
    username: str
    full_name: str
    role: str
    password_hash: str
    status: str = "ACTIVE"


class UserService:
    def __init__(self, store: CSVStore):
        self.store = store
        self.audit = Stack()
        self._bst = BST()
        self._list = LinkedList()
        self._reload()

    def _reload(self):
        self._bst = BST()
        self._list = LinkedList()
        for r in self.store.read_all():
            u = User(
                username=r["username"],
                full_name=r.get("full_name", ""),
                role=r.get("role", "CONSULTA"),
                password_hash=r.get("password_hash", ""),
                status=r.get("status", "ACTIVE"),
            )
            self._bst.insert(u.username.strip().lower(), u)
            self._list.append(u)

    def ensure_admin(self):
        if self.get_by_username("admin"):
            return
        self.create_user("admin", "Administrador", "ADMIN", "admin123")
        self.audit.push("Se creó usuario admin por defecto (admin/admin123).")

    def list_users(self) -> List[User]:
        return self._bst.inorder()

    def get_by_username(self, username: str) -> Optional[User]:
        if not username:
            return None
        return self._bst.search(username.strip().lower())

    def create_user(self, username: str, full_name: str, role: str, password_plain: str) -> User:
        username_norm = username.strip().lower()
        if self.get_by_username(username_norm):
            raise ValueError("El usuario ya existe.")

        u = User(
            username=username_norm,
            full_name=full_name.strip(),
            role=role.strip().upper(),
            password_hash=generate_password_hash(password_plain),
            status="ACTIVE",
        )

        rows = self.store.read_all()
        rows.append({
            "username": u.username,
            "full_name": u.full_name,
            "role": u.role,
            "password_hash": u.password_hash,
            "status": u.status,
        })
        self.store.write_all(rows)
        self._reload()

        self.audit.push(f"Creado usuario: {u.username} ({u.role})")
        return u

    def validate_login(self, username: str, password_plain: str) -> Optional[User]:
        u = self.get_by_username(username)
        if not u:
            return None
        if u.status != "ACTIVE":
            return None
        if not check_password_hash(u.password_hash, password_plain):
            return None
        return u

    def audit_tail(self, limit: int = 15):
        return self.audit.to_list()[:limit]