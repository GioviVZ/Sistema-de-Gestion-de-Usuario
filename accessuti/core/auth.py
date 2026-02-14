from flask import session

def login_user(user_dict: dict):
    session["user"] = user_dict

def logout_user():
    session.pop("user", None)

def current_user():
    return session.get("user")