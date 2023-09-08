from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "../database/llanwrydd.db"

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    # connect to database
    db.init_app(app)

    from .view import views

    app.register_blueprint(views, url_prefix='/')

    return app

