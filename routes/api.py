from . import *

api_bp = Blueprint('api', __name__, url_prefix='/api')

from flask import request, jsonify
from utils.dockers import *
from utils.api_page import ApiPage

@api_bp.route('/', methods=['GET'])
def test_connection():
    ap  = ApiPage(response='Connection test successful.')
    return ap.createResponse()

@api_bp.route('/info', methods=['GET'])
def get_docker_info():
    ap = ApiPage(response=client.info())
    return ap.createResponse()
    

@api_bp.route('/df', methods=['GET'])
def get_docker_df():
    ap = ApiPage(response=client.df())
    return ap.createResponse()

# 取得所有容器
@api_bp.route('/containers', methods=['GET'])
def get_containers():
    ap = ApiPage(response=get_all_containers())
    return ap.createResponse()

@api_bp.route('/containers/<container_id>', methods=['GET'])
def get_container(container_id):
    ap = ApiPage(response=Container(container_id).container.stats(stream =False))
    return ap.createResponse()

# 建立新容器（POST）
@api_bp.route('/containers', methods=['POST'])
def create_container():
    data = request.get_json()
    result = run_container(data)
    return jsonify(result), 201 if result['status'] == 'started' else 400

# 刪除容器（DELETE）
@api_bp.route('/containers/<string:name>', methods=['DELETE'])
def delete_container_api(name):
    result = delete_container(name)
    status = 200 if result['status'] == 'deleted' else 404
    return jsonify(result), status
