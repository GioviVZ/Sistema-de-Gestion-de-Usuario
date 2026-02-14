from flask import Flask
from .config import Config
from .storage.csv_store import CSVStore
from .services.user_services import UserService
from .routes.auth_routes import auth_bp
from .routes.user_routes import users_bp

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)

    # Store + Service
    store = CSVStore(app.config["USERS_CSV"])
    svc = UserService(store)
    svc.ensure_admin()

    # Guardar el servicio dentro del app (simple)
    app.extensions["user_service"] = svc

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)