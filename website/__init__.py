from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'aldskfhlsd lakdshflk'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{path.join(path.dirname(path.abspath(__file__)), DB_NAME)}'
    db.init_app(app)

    # Import and register Blueprints
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import models to ensure they're registered with SQLAlchemy
    from .models import User, Student, SchoolClass, Subject, Grade

    # Create the database if it doesn't exist
    create_database(app)

    # Set up Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

def create_database(app):
    db_path = path.join(path.dirname(path.abspath(__file__)), DB_NAME)
    if not path.exists(db_path):
        with app.app_context():
            db.create_all()
        print('Created Database')
