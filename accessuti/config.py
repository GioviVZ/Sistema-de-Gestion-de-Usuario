import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-me")

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    USERS_CSV = os.environ.get("USERS_CSV", os.path.join(BASE_DIR, "data"))