from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.secret_key = 'somesecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sitedata.sqlite'

    db.init_app(app)

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Import models AFTER db.init_app(app)
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.scalar(db.select(User).where(User.id == user_id))

    # ✅ Import and register blueprints *inside* the create_app function
    from . import views
    app.register_blueprint(views.mainbp)

    from . import auth
    app.register_blueprint(auth.authbp)

    from .events import destbp
    app.register_blueprint(destbp)

    return app
