# travel/__init__.py
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # --- Config ---
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-change-me"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///traveldb.sqlite"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        # Store uploads under the app root, not a leading slash path
        UPLOAD_FOLDER=os.path.join(app.root_path, "static", "image"),
        # Nice-to-have limits
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16 MB
    )

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Extensions
    Bootstrap5(app)
    db.init_app(app)

    # Login manager
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to continue."
    login_manager.login_message_category = "info"

    from .models import User  # import here to avoid circulars

    @login_manager.user_loader
    def load_user(user_id):
        # SQLAlchemy 2.x style lookup
        return db.session.get(User, int(user_id))

    # Blueprints
    from . import views
    app.register_blueprint(views.mainbp)

    from . import events
    app.register_blueprint(events.destbp)   # this is your 'event' blueprint

    from . import auth
    app.register_blueprint(auth.authbp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html", error=e), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        # make sure a failed transaction doesn't poison later requests
        try:
            db.session.rollback()
        except Exception:
            pass
        return render_template("500.html", error=e), 500

    # Optional: auto-create tables for dev/student environments
    with app.app_context():
        db.create_all()

    return app
