from . import *
from platform import system,node
from utils.g import clients

server_bp = Blueprint('server', __name__, url_prefix='/server')

@server_bp.route('/')
def index():
    return redirect('/server/info')

@server_bp.route('/info', methods=['GET'])
# @login_required
def info():
    data = [
        ['伺服器名稱', node()],
        ['伺服器系統', system()], 
        ['伺服器啟動時間', current_app.config['SERVER_RUN_TIME']],
        ['目前連線數',len(clients)],
        ['目前連線IP', str('、'.join(clients))],
    ]
    return render_template('common/list.html', title='伺服器資訊',heads=['Key','Value'],datas=data)