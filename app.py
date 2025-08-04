
#? sudo python3 app.py
#? sudo pip3 freeze > requirements.txt

from flask import Flask

###* Global Variable ###
from utils.g import clients
from utils.utils import now_time

###* Register Blueprint ###
from routes import APP, socketio
from routes import *

from werkzeug.exceptions import HTTPException
@APP.errorhandler(HTTPException)
def all_error_handler(e:HTTPException):
    # abort(status_code, response=f"{status_code}")
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


@APP.teardown_request
def remove_client(exc=None):
    """Removes the client from the set clients when the request is finished."""
    for ip, timestamp in list(clients.items()):
        if time() - timestamp > 300:  # 5 minutes
            del clients[ip]


# APP.run(
#     host='0.0.0.0',
#     port=80, 
#     debug=True
# )

socketio.run(
    app = APP,
    host = '0.0.0.0',
    port = 80, 
    debug = True
)