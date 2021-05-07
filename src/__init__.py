from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from src.config import Config
from flask import jsonify

# Binding Extentions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.sign_in'
login_manager.login_message_category = 'info',
mail = Mail()


def create_app(config_class=Config):
    # Initializing the flask app
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initializing Extensions for the app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from src.components.main.routes import main
        from src.components.users.routes import users
        from src.components.posts.routes import posts
        from src.components.errors.handlers import errors
        db.create_all()  # Create sql tables for our data models

    


    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(errors)

    return app