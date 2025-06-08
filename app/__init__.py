from flask import Flask
from flask_login import LoginManager
from .models import User
from .routes import routes_bp
from .payment import payment_bp
from .auth import auth_bp

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def create_app(SECRET_KEY):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY

    login_manager.init_app(app)

    app.register_blueprint(routes_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(auth_bp)

    @app.template_filter('format_currency')
    def format_currency_filter(value):
        return f"{value:.2f}"

    return app