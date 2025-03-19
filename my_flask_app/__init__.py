from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"

    db.__init__(app)

    loginmanager=LoginManager()
    loginmanager.login_view='auth.login'
    loginmanager.init_app(app)

    from .models import User
    @loginmanager.user_loader
    def load_user(user_id):
        User.query.get(int(user_id))

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
    