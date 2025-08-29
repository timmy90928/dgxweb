
###* Login Manager ###
#? https://ithelp.ithome.com.tw/articles/10328420
from flask_login import login_user
from flask_login import login_required 
from flask_login import logout_user 

###* Register Blueprint ###
from .admin import initAdmin
from .index import index_bp
from .container import container_bp
from .image import image_bp
from .api import api_bp
from .server import server_bp
from .chat import chat_bp

ALL_BP = [index_bp, api_bp, server_bp, container_bp, image_bp, chat_bp]

