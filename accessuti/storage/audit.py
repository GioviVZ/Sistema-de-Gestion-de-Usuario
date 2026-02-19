# app/storage/audit.py
import os, json
from datetime import datetime

def _now_iso():
    return datetime.now().isoformat(timespec="seconds")

class AuditLogger:
    def __init__(self, logs_dir: str):
        self.logs_dir = logs_dir
        os.makedirs(self.logs_dir, exist_ok=True)
        self.text_path = os.path.join(self.logs_dir, "audit.log")
        self.jsonl_path = os.path.join(self.logs_dir, "audit.jsonl")

    def log(self, action: str, actor="unknown", ip="-", meta=None):
        meta = meta or {}
        event = {"ts": _now_iso(), "action": action, "actor": actor, "ip": ip, "meta": meta}

        with open(self.text_path, "a", encoding="utf-8") as f:
            f.write(f"[{event['ts']}] action={action} actor={actor} ip={ip} meta={meta}\n")

        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")