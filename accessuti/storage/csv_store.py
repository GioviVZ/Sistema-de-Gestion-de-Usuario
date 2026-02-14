import csv
import os
from typing import List, Dict

FIELDS = ["username", "full_name", "role", "password_hash", "status"]


class CSVStore:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=FIELDS)
                w.writeheader()

    def read_all(self) -> List[Dict]:
        with open(self.csv_path, "r", newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            return list(r)

    def write_all(self, rows: List[Dict]) -> None:
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            for row in rows:
                w.writerow({k: row.get(k, "") for k in FIELDS})