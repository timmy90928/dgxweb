from application import *
from . import *
from utils.dockers import Image, Container
from utils.g import current_user


image_bp = Blueprint('image', __name__, url_prefix='/image')

@image_bp.route('/all')
def all_images():
    ai = Image().list()
    heads = ai[0]
    datas = ai[1:]

    return render_template(
        'common/list.html', title = 'All Images', heads = heads, datas = datas,
        left = f"{len(datas)} images", 
    )

@socketio.on('create_container_by_image')
def handle_docker_pull(data):
    """
    當收到前端 'create_container_by_image' 事件時，此函數會被觸發
    """
    client_sid = request.sid 
    image_to_pull = data.get('image')

    if image_to_pull:
        # 避免阻塞主程式
        socketio.start_background_task(
            target = Container.create, 
            image_name = image_to_pull, 
            user = vars(current_user), 
            sid = client_sid
        )