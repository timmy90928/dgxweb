from .config import configs
from .model import db, _create_sqlite_uri
from typing import Literal

###* Standard Library ###
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
from flask_socketio import SocketIO, emit
import requests
from threading import Thread
from time import sleep

###* utils ###
from loguru import logger
from os import urandom
from utils.utils import errorCallback
from utils.utils import now_time
from utils.utils import get_ssh_key
from utils.utils import hash
from application.model import _create_sqlite_uri

###* Global Variable ###
from utils.g import rootdir
from utils.g import clients

###* Main App ###
APP = Flask("DGX")

###* Login Manager ###
from flask_login import LoginManager
login_manager = LoginManager(APP)
login_manager.login_view = '/login'

###* Init Jinja ###
from utils.jinja_func import initJinjaFunc
initJinjaFunc(APP)

###* Login Manager ###
#? https://ithelp.ithome.com.tw/articles/10328420
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

from werkzeug.exceptions import HTTPException
@APP.errorhandler(HTTPException)
def all_error_handler(e:HTTPException):
    from utils.g import current_user
    user = f"{current_user.name}<{current_user.username}>" if current_user.is_authenticated else "未登入"
    ip = request.remote_addr
    logger.exception(f"[{ip}({user})] {e}")
    page = [
        ['HTTP狀態碼', e.code],
        ['HTTP狀態', e.name],
        ['錯誤訊息', str(e.description)],
        ['回覆(response)', str(e.response)],
        # ['標頭(headers)', str(e.get_headers())],
        # ['參數(args)', str(e.args if e.args else '')],
    ]
    return render_template('common/list.html',title=f"{e.code}-{e.name}",datas=page,heads=['key', 'value']), e.code

from time import time

@APP.before_request
def track_connection() -> None:
    """Tracks all the current clients (by IP) and stores them in the set clients."""
    ip = request.remote_addr
    clients[ip] = time()

from flask import Response
@APP.after_request
def log_request(response:Response) -> None:
    from utils.g import current_user
    ip = request.remote_addr
    if not (300 <= response.status_code < 400):
        user = f"{current_user.name}<{current_user.username}>" if current_user.is_authenticated else "未登入"
        logger.info(f"[{ip}({user})] {request.method} {request.full_path}")
    return response


@APP.teardown_request
def remove_client(exc=None):
    """Removes the client from the set clients when the request is finished."""
    for ip, timestamp in list(clients.items()):
        if time() - timestamp > 300:  # 5 minutes
            del clients[ip]

def create_app(config_name:Literal['development', 'production', 'testing'] = 'production'):
    global APP

    ###* Logger ###
    from sys import stderr
    config = {
        "handlers": [
            {"sink": stderr, "level": "DEBUG"},
        ],
    }
    logger.configure(**config)
    logger.add(
        f"dgx_{config_name}.log", level="INFO", retention="5 days"
    )

    ###* Configurations ###
    logger.info(f"Start by {config_name}")
    APP.config.from_object(configs[config_name])

    ###* Sqlite ###
    from application.model import initDB
    initDB(APP) # Database (SQLAlchemy)

    ###* Register Blueprint ###
    from routes import ALL_BP
    from routes.admin import initAdmin
    for bp in ALL_BP:
        APP.register_blueprint(bp)

    ###* Init Tools ###
    initJinjaFunc(APP)  # Jinja2
    initAdmin(APP)      # Admin View

    ###* SocketIO ###
    socketio = SocketIO(APP, cors_allowed_origins="*", async_mode='eventlet')

    return socketio