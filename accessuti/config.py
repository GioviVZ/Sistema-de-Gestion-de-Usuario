import os

class Config:
    SECRET_KEY = "supersecretkey"
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    USERS_CSV = os.path.join(BASE_DIR, "data", "users.csv")