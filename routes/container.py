
from . import *
from utils.dockers import Container, Image, get_all_containers, client
from utils.model import Container as ContainerDB, User as user_db
from utils.utils import Token
from utils.g import current_user
from pathlib import Path
import subprocess
container_bp = Blueprint('container', __name__, url_prefix='/container')

@container_bp.route('/all')
def all_containers():
    if current_user.rolenum <= 1:
        ac = Container().list(with_control=True)
        right = "<a href='/container/create' class='small-blue-button'>新增</a>"
    elif current_user.is_authenticated:
        ac = Container(current_user.username).list(with_control=True)
        right = "<a href='/container/create' class='small-blue-button'>新增</a>"
    else:
        ac = Container().list()
        right = None

    heads = ac[0]
    datas = ac[1:]
    return render_template('common/list.html', title = 'All Containers', heads = heads, datas = datas, left = f"{len(datas)} containers", right=right)

@container_bp.route('/create', methods=['GET', 'POST'])
def container_create():
    if request.method == 'POST':
        image_name = request.form.get('image')
        Container.create(current_user.username, image_name)

        return redirect('/container/all')
    images = [
        ['nvcr.io/nvidia/pytorch:24.05-py3'],
        ['nvcr.io/nvidia/tensorflow:24.05-tf2-py3'],
        ['nvcr.io/partners/matlab:r2024a'],
        ['nvcr.io/partners/matlab:r2019b']
    ]
    return render_template('container_create.html', images = images)

@container_bp.route('/stop/<container_id>')
def container_stop(container_id):
    ###* Search for container with <container_id> ###
    container = Container(container_id).container

    ###* Stop container ###
    container.stop(timeout=5)
    container.reload() 

    return redirect('/container/all')

@container_bp.route('/start/<container_id>')
def container_start(container_id):
    ###* Search for database and container with <container_id> ###
    container_db:ContainerDB = ContainerDB.query.filter_by(container_id=container_id).first()
    container = Container(container_id).container

    ###* Generate a random token from a personal password ###
    password = container_db.user.password
    token = Token(urandom(32).hex()).generate(hash(password))

    ###* Put the token into the database of this container ###
    container_db.password = token
    db.commit()

    ###* Start container ###
    container.start()
    container.exec_run(
        f"jupyter lab --allow-root --ip 0.0.0.0 --no-browser --NotebookApp.token='{token}'",
        detach=True # Run in the background
    )
    container.reload() 

    return redirect('/container/all')

@container_bp.route('/remove/<container_id>')
def container_remove(container_id):
    ###* Search for database and container with <container_id> ###
    container_db:ContainerDB = ContainerDB.query.filter_by(container_id=container_id).first()
    container = Container(container_id).container
    client.images.prune()

    container.remove()
    db.delete(container_db)

    Path(f'/home/lab120/user_data/{current_user.username}').rmdir()

    return redirect('/container/all')
