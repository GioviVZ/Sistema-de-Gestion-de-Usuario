from dataclasses import dataclass
from datetime import datetime

@dataclass
class AuditEvent:
    ts: str
    actor: str
    action: str

class Stack:
    def __init__(self):
        self._data = []

    def push(self, item):
        self._data.append(item)

    def to_list(self):
        return list(reversed(self._data))

def audit_event(action, actor="system"):
    return AuditEvent(
        ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        actor=actor,
        action=action
    )