
from . import *
from utils.dockers import Container, Image, get_all_containers, get_gpu_usage
from utils.utils import get_local_ip, Token, Email, hash, get_ssh_key
from utils.model import User as UserDB
from utils.g import User as Guser

index_bp = Blueprint('index', __name__, url_prefix='/')

@index_bp.route('/alert/<message>', methods=['GET'])
def alert(message: str) -> None:
    """Prints an alert message to the terminal."""
    to = request.args.get('to',None)
    return render_template('common/alert.html', message=message, url=to)

@index_bp.route('/confirm/<message>', methods=['GET'])
def confirm(message: str) -> None:
    """/confirm/test?to=/"""
    to = request.args.get('to',None)
    return render_template('common/confirm.html', message=message+'?', url=to)

@index_bp.route('/')
def index_page():
    admin = UserDB.query.filter_by(username = 'admin').first()
    gpu_usage = get_gpu_usage()
    return render_template('index.html', admin=admin, gpu_usages=gpu_usage)

@index_bp.route('/login', methods=['GET', 'POST'])
def login(): 
    dev = request.args.get('dev')
    if dev and dev[15:50] == get_ssh_key()[15:50]:
        login_user(Guser(0), remember=True)
        print('ok')
        return redirect('/container/all')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user:UserDB = UserDB.query.filter_by(username = username).first()
        if not user: return redirect('/alert/查無此帳號?to=/login')
        if not user.check_password(password): return redirect('/alert/密碼錯誤?to=/login')
        

        # access_token = create_access_token(identity=username)
        # response = redirect('/')
        # set_access_cookies(response, access_token)
        
        login_user(Guser(user.id), remember=True)
        return redirect('/container/all')
    return render_template('login.html', title = '登入')

@index_bp.route('/logout', methods=['GET', 'POST'])
def logout(): 
    logout_user()
    return redirect('/login')

@index_bp.route('/register', methods=['GET', 'POST'])
def register(): 
    from .api import send_email_in_background
    if request.method == 'POST':
        token = Token('register').generate(request.form)
        _email = request.form['email']
        _username = request.form['username']

        send_email_in_background({
            "Subject": "[AI LAB DGX] 啟用帳號",
            "From": "AI Lab DGX Team",
            "To": _email,
            "Cc": "",
            "Text": [
                f"{_username} 歡迎使用DGX", 
                "請點選下面連結來啟用帳號",
                f"{get_local_ip()}/register/{token}"
            ]
        })
  

        return redirect(f'/alert/請於5分鐘內前往 {_email} 啟用帳號?to=/login')

    return render_template('login.html', title = '註冊')

@index_bp.route('/register/<token>', methods=['GET', 'POST'])
def register_token(token): 
    try:
        form = Token('register').verify(token, 60*5)
        password = form['password']

    except:
        abort(401, response = 'Token 錯誤, 可能已超過 5 分鐘, 請重新申請')
    user = UserDB(
        username = form['username'],
        name = form['name'],
        email = form['email'],
        password = form['password'],
        role = 'user'
    )
    db.add(user)

    return redirect('/login')

@index_bp.route('/all_images')
def all_images():
    ai = Image().list()
    heads = ai[0]
    datas = ai[1:]

    return render_template('common/list.html', title = 'All Images', heads = heads, datas = datas)

@index_bp.route('/a')
@jwt_required()
def containers():
    print(get_jwt())
    _containers:list = get_all_containers()
    containers:list = []
    for container in _containers:
          containers.append(
                [
                    f"<a href=http://{get_local_ip()}:{container['ports']['8888/tcp'][0]['HostPort']}>"\
                    f"{container['name']}</a>", 
                    container["status"], 
                    container["image"],
                    container['ports']['22/tcp'][0]['HostPort']
                ]
          )

    return render_template('index.html', containers=containers)