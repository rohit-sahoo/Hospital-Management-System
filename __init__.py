from flask import Flask
from HospitalSystem.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import logging

app = Flask(__name__)
config = Config()

app.config['SECRET_KEY'] = config.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db : SQLAlchemy = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

db.init_app(app)
login_manager.init_app(app)

from HospitalSystem import routes