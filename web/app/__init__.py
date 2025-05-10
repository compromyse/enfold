from flask import Flask
from flask_login import LoginManager
from .models import User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .auth import auth as auth_blueprint
    from .main import main as main_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
