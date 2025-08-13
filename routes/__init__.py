from flask import Flask
from flask import Blueprint
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
from flask import make_response
from flask import session #? session['key'] = 'value'
from flask import abort
from flask import send_file
from flask import jsonify
from flask import Response
from flask import current_app
from flask import g
import requests
from threading import Thread
from time import sleep

###* utils ###
from os import urandom
from utils.utils import errorCallback
from utils.utils import now_time
from utils.utils import get_ssh_key
from utils.utils import hash
from utils.model import _create_sqlite_uri
from utils.g import rootdir

APP = Flask("DGX")
APP.config['TITLE'] = 'AI LAB DGX'
APP.config['SECRET_KEY'] = get_ssh_key()
APP.config['SERVER_RUN_TIME'] = now_time()
APP.config['JWT_SECRET_KEY'] = urandom(32).hex()
APP.config["JWT_TOKEN_LOCATION"] = ["cookies"] # Tell Flask-JWT-Extended to expect the token in cookies
APP.config["SQLALCHEMY_DATABASE_URI"] = _create_sqlite_uri(rootdir.joinpath('dgx.db'))
APP.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

###* Init Jinja ###
from utils.jinja_func import initJinjaFunc
initJinjaFunc(APP)

###* Login Manager ###
#? https://ithelp.ithome.com.tw/articles/10328420
from flask_login import login_user
from flask_login import login_required 
from flask_login import logout_user 
from flask_login import LoginManager

login_manager = LoginManager(APP)
login_manager.login_view = '/login'

@login_manager.user_loader
def load_user(username):
    
    from utils.g import User
    return User(username)

###* jwt ###
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_jwt_extended import set_access_cookies

jwt = JWTManager(APP)

###* ###
from flask_socketio import SocketIO, emit
socketio = SocketIO(APP, cors_allowed_origins="*", async_mode='eventlet')

###* Sqlite ###
from utils.model import db
db.init_app(APP)
with APP.app_context():
    db.create_all()

###* Register Blueprint ###
from .admin import initAdmin
from .index import index_bp
from .container import container_bp
from .api import api_bp
from .server import server_bp
from .chat import chat_bp

initAdmin(APP)
ALL_BP = [index_bp, api_bp, server_bp, container_bp, chat_bp]

for bp in ALL_BP:
    APP.register_blueprint(bp)