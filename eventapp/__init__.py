from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
db=SQLAlchemy()

def create_app():

     # A secret key for the session object
    app.secret_key = 'somerandomvalue'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///traveldb.sqlite'
    db.init_app(app)

    # we use this utility module to display forms quickly
    Bootstrap5(app)

    

    login_manager = LoginManager()
      #set the name of the login function that lets user login
    # in our case it is auth.login (blueprintname.viewfunction name)
    login_manager.login_view='auth.login'
    login_manager.init_app(app)

   

    

    #config upload folder
    UPLOAD_FOLDER = '/static/image'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    

    #create a user loader function takes userid and returns User
    from .models import User  # importing here to avoid circular references
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    
    # add Blueprints
    from . import views
    app.register_blueprint(views.mainbp)
    from . import events
    app.register_blueprint(events.destbp)
    from . import auth
    app.register_blueprint(auth.authbp)

    # ERROR HANDLING
    @app.errorhandler(404)
    def not_found(e):
      return render_template("404.html", error=e)

    @app.errorhandler(500)
    def internal_server_error(e):
      return render_template("500.html", error=e), 500

    return app
