from flask import session

def current_user():
    return session.get("user")