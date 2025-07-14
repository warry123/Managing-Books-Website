from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


#initialising SQLAlchemy
db = SQLAlchemy()
DB_NAME = "database7.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'warrysworld'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)


    #initialising routes or pages
    from .views import views
    from .auth import auth


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')


    #initialising database
    from .models import User, Books, BooknGenre, Favourites, BestAuthors
    create_database(app)


    #initialising flask-login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app


#create database method
def create_database(app):
    if not path.exists('COMPSCI IA 2/instance/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print("Database Created!")
