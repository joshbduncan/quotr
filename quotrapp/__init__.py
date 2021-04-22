from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from quotrapp.config import Config


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users_bp.login'
login_manager.login_message_category = "warning"
limiter = Limiter(key_func=get_remote_address)
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)

    from quotrapp.users.routes import users_bp
    from quotrapp.quotes.routes import quotes_bp
    from quotrapp.main.routes import main_bp
    from quotrapp.errors.handlers import errors_bp
    from quotrapp.api.routes import api_bp
    app.register_blueprint(users_bp)
    app.register_blueprint(quotes_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(api_bp)

    return app
