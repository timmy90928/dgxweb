from utils.utils import now_time, timestamp
from flask import  Response, request, abort
from json import dumps
from werkzeug.http import HTTP_STATUS_CODES
from typing import Optional, Callable, Any

# def r500(msg, note='Exception'):
#     ap = api_page(500, note)
#     ap.json["status"] = "Internal Server Error"
#     ap.error_message = msg
#     return ap.createResponse()

def jsonify(obj):
    jsonify_config = {"sort_keys": False, "indent": 4,'ensure_ascii':False}
    json_data = dumps(obj, **jsonify_config)
    return Response(json_data, mimetype='application/json')

class ApiPage:
    def __init__(self, status_code:int = 200, response = None):
        self.status_code = status_code # https://zh.wikipedia.org/zh-tw/HTTP%E7%8A%B6%E6%80%81%E7%A0%81
        self.response = response or {}
        
        self.datas = None
        self.error_message = None
        self.Authorization = request.headers.get('Authorization', None)
        self.method = request.method

        self.json = self.get_base_json()

    def __setitem__(self, key, value):
        self.response[key] = value

    def get_base_json(self):
        nt = now_time()
        base_json = {
            'method': self.method,
            'status_code': self.status_code,
            'status': HTTP_STATUS_CODES.get(self.status_code,"Unknown Error"),
            "time": nt,
            "timestamp": timestamp(string=nt),
            'response': self.response,
        }
        return base_json

    def createResponse(self):
        if self.datas: self.json.update({'datas': self.datas})
        if self.error_message: self.json.update({'error_message': self.error_message})
        return jsonify(self.json), self.status_code

from functools import wraps
def errorCallback(note):
    def decorator(func:Callable):
        @wraps(func)
        def wrap(*args, **kwargs):
            try:
                return func(*args, **kwargs)   # print(func.__name__)
            except Exception as e:
                abort(500, description=f"[{e.__class__.__name__} ({func.__name__})] {e}",  response=note)
        return wrap
    return decorator