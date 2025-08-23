# from configparser import ConfigParser
from pathlib import Path
from enum import IntEnum as _IntEnum



clients = {}
"""
The IP address of the server currently used.
"""

rootdir = Path(__file__).parent.parent
"""
The root directory.
"""

class roles(_IntEnum):
    developer = 0
    admin = 1
    user = 2
    viewer = 3
    error = 9

from flask_login import UserMixin as _UserMixin
from flask_login import current_user as _current_user

class User(_UserMixin):
    #? def __init__(self, user_id:int, user_name:str, nickname:str, role:str = 'admin'):
    def __init__(self,user_id:int):
        user_id = int(user_id)
        if user_id == 0:
            username,name,role, email = 'developer','開發人員','developer','developer'
        else:
            try:  
                from application.model import User as UserDB
                user:UserDB = UserDB.query.filter_by(id = user_id).first()
                name = user.name
                username = user.username
                email = user.email
                role = user.role
            except Exception as e:  
                name = e
                username = 'error'
                email = 'error'
                role = 'error'

        self.id:int = user_id
        self.username = username
        self.name = name
        self.email = email
        self.role = role
        self.rolenum = roles[role].value
current_user:User = _current_user
