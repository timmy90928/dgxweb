from application import *

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

#* Send Email
from utils.utils import Email
@api_bp.route('/sendemail', methods=['POST'])
def sendemail():
    """
    ```json
    {
        "Subject": "[AILAB DGX] 啟用帳號",
        "From": "AI Lab DGX Team", # Optional
        "To": ["weiwen@alum.ccu.edu.tw"],
        "Cc": [""],
        "Bcc": [""],
        "Text": [
            "第一段", 
            "第二段"
        ]
    }
    ```
    """
    json:dict = request.get_json()

    to = json.get('To', [])
    cc = json.get('Cc', [])
    bcc = json.get('Bcc', [])

    to_list = to if isinstance(to, list) else [to]
    cc_list = cc if isinstance(cc, list) else [cc]
    bcc_list = bcc if isinstance(bcc, list) else [bcc]

    all_recipients = to_list + cc_list + bcc_list 

    # 確保收件人列表不為空
    if not all_recipients:
        ap = ApiPage(response={"status": "error", "message": "No recipients provided"})
        return ap.createResponse() 

    with Email(all_recipients) as email:
        text = json['Text']
        text =  text if len(text) == 0 else "\n".join(text)
        msg = email.getText(
            f"{text}\n\nAILAB DGX TEAM" if request.remote_addr == '127.0.0.1' else f"{text}\n\n此訊息由 {request.remote_addr} 使用 AILAB DGX API 發出"
        )

        msg['Subject'] = json.get('Subject', '')
        msg['From'] = json.get('From', 'AILAB DGX TEAM' if request.remote_addr == '127.0.0.1' else 'AILAB DGX API')
        msg['To'] = ", ".join(to_list)
        msg['Cc'] = ", ".join(cc_list)

        status = email.sendMessage(msg.as_string())
        ap = ApiPage(response = status)
        return ap.createResponse()

def send_email_in_background(json_data):
    """No waiting for delays in sending mail."""
    def sendemail_thread(json_data):
        sleep(1) # To prioritize alert.
        return requests.post( # Using this system's API.
            'http://localhost/api/sendemail', json = json_data, timeout = 10
        )
    Thread(
        target=sendemail_thread, args=(json_data,)
    ).start()

#* Identity Authentication
from application.model import User as UserDB
@api_bp.route('/auth', methods=['POST'])
def auth():
    """
    ```json
    {
        "username": "...",
        "password": "..."
    }
    ```
    """
    json:dict = request.get_json()
    user_db:UserDB = UserDB.query.filter_by(username=json['username']).first()
    if not user_db:
        ap = ApiPage(404, response = f"{json['username']} user not found.")
    elif user_db.check_password(json['password']):
        ap = ApiPage(response={
            'name': user_db.name,
            'email': user_db.email
        })
    else:
        ap = ApiPage(401, response = f"{user_db.name}'s identity authentication failed.")

    return ap.createResponse()