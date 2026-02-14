import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    DATA_DIR = os.getenv("DATA_DIR", "data")
    USERS_CSV = os.getenv("USERS_CSV", os.path.join(DATA_DIR, "users.csv"))