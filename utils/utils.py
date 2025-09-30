from datetime import timedelta,datetime,timedelta

from base64 import b64encode,b64decode
from urllib.parse import quote, unquote
from typing import Any, Union, Optional, Callable, Sequence, overload
from typing_extensions import Self
from hashlib import sha3_256
from socket import socket, AF_INET, SOCK_DGRAM
from itsdangerous import URLSafeTimedSerializer

from utils.g import rootdir, current_user
from flask_login import login_required as _login_required
from flask import current_app

###* File ###
from pathlib import Path
from  pickle import (
    dump as _pickle_dump,
    load as _pickle_load
)
from json import (
    load as _json_load, 
    dump as _json_dump
)

#* Email
from smtplib import SMTP
from email.mime.text import MIMEText

def now_time() -> str:
    """
    ## Example
    >>> now_time() # doctest: +SKIP
    '2022-08-31 23:59:59'
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def hash(text:str) -> str:
    """
    Hash the text using SHA3-256.

    ## Example
    >>> hash('home')
    'a20243f409be1afca9a63f66224b3467eaa9194753561e33b4d1202294cabd21'
    """
    return str(sha3_256(text.encode()).hexdigest())

import re
def timestamp(year=1999, month=1, day=1, hour=0, minute=0, second=0, dday=0, dhour=0, dminute=0, dsecond=0, ts:Union[int,float] = None, iso:str = None, string:str = None) -> float:
    """
    ## Example
    >>> timestamp(2024,10+1,dsecond=-1)
    1730390399.0
    >>> timestamp(string='2024-10-31 23:59:59')
    1730390399.0
    >>> timestamp(ts=1730390399.0)
    '2024-10-31 23:59:59'
    """
    if ts:
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    elif iso:
        iso = iso.replace('Z', '')  # 去掉結尾的 Z
        match = re.match(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6})", iso)
        if match:
            truncated_iso = match.group(1)
        else:
            truncated_iso = iso.split('.')[0] if '.' in iso else iso


        iso_time = datetime.fromisoformat(truncated_iso)
        return iso_time.strftime('%Y-%m-%d %H:%M:%S')
    elif string:
        arr_string = string.split(" ")
        if len(arr_string) == 1:
            arr = arr_string[0].split("-")
            return timestamp(year=int(arr[0]), month=int(arr[1]), day=int(arr[2]))
        else:
            arr0 = arr_string[0].split("-")
            arr1 = arr_string[1].split(":")
            return timestamp(year=int(arr0[0]), month=int(arr0[1]), day=int(arr0[2]),hour=int(arr1[0]), minute=int(arr1[1]), second=int(arr1[2]))
    else:
        dt = timedelta(days=dday, hours=dhour, minutes=dminute, seconds=dsecond)
        t = datetime.strptime(f'{year:04}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}', "%Y-%m-%d %H:%M:%S") + dt
        return t.timestamp()

def get_local_ip():
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google Public DNS
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

def format_bytes(bytes_value):
    if bytes_value < 1024:
        return f"{bytes_value} B"
    elif bytes_value < 1024**2:
        return f"{bytes_value / 1024:.2f} KB"
    elif bytes_value < 1024**3:
        return f"{bytes_value / (1024**2):.2f} MB"
    else:
        return f"{bytes_value / (1024**3):.2f} GB"
    
class base64:
    """
    Base64 encoding and decoding.

    ## Example
    >>> value_str = 'abcde'
    >>> value_list = ['ac','cd']
    >>> b64_str = base64(value_str).encode()
    >>> b64_list = base64(value_list).encode()
    >>> b64_str
    'YWJjZGU%3D'
    >>> b64_list
    'YWMsY2Q%3D'
    >>> base64(b64_str).decode()
    'abcde'
    >>> base64(b64_list).decode()
    ['ac', 'cd']
    """
    # __slots__ = ("data",)

    def __init__(self, data: Union[str,list]) -> None:
        self.data = str(','.join(data))  if isinstance(data, list) else str(data)

    def encode(self) -> str:
        """Encode the stored data to a base64 string."""
        b64 = b64encode(self.data.encode()).decode("utf-8")
        return quote(b64)

    def decode(self) -> Union[str, list[str]]:
        """
        Decode the stored base64 string to the original string.

        Returns a list of strings if the original data was a list, otherwise a single string.
        """
        decoded_string = b64decode(unquote(self.data)).decode()
        return decoded_string.split(",") if "," in decoded_string else decoded_string
    
from typing import Optional, Callable, Any
from functools import wraps
from flask import abort
def errorCallback(note:Optional[str]=None, code:int = 500):
    """
    https://zh.wikipedia.org/zh-tw/HTTP%E7%8A%B6%E6%80%81%E7%A0%81
    """
    def decorator(func:Callable):
        @wraps(func)
        def wrap(*args, **kwargs):
            try:
                return func(*args, **kwargs)   # print(func.__name__)
            except Exception as e:
                abort(code, description=f"[{e.__class__.__name__} ({func.__name__})] {e}",  response=note)
        return wrap
    return decorator

def strip_whitespace(text: str) -> str:
    """
    Remove all whitespace characters from a given string.

    This function will replace 3 types of whitespace characters in a given string with an empty string:

    1. The normal space character (`` ` ``)
    2. The non-breaking space character (`` ``)

    >>> strip_whitespace('  hello  world  ')
    'helloworld'
    """
    
    return text.replace(' ','').replace(' ','').replace('\u202f','').replace('\u2009','')

def get_ssh_key(name:str = 'dgx.pub'):
    key_path = Path('/home/lab120/.ssh').joinpath(name)
    with open(key_path, 'r', encoding='utf-8') as f:
        secret_key_content = f.read()
    return secret_key_content

class Token(URLSafeTimedSerializer):
    """```
    >>> tkn = Token()
    >>> token = tkn.generate({'user':'timmy'})
    >>> datas = tkn.verify(token, 1)

    ```"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None: 
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, salt:str = None):
        super().__init__(get_ssh_key(), salt)

    def generate(self, datas):
        return self.dumps(datas)
    
    def verify(self, token, expire_seconds=None):
        """

        Raises:
            SignatureExpired: Link expired.
            BadTimeSignature: Invalid token.

        """
        return self.loads(token, max_age=expire_seconds)

class Email(SMTP):
   
    def __init__(
            self, 
            to_addr:Union[str, Sequence[str]],
            from_addr_pwd:tuple = ("ailab@ee.ccu.edu.tw", "bung ovhd rrcu nayg")
        ) -> None:
        """
        Args:
            to_addr (str, Sequence[str]): Target Address
            
        Example:
            ```
            with Email("weiwen@alum.ccu.edu.tw") as email:
                msg = email.getText("This is a test email sent from Python.")

                msg['Subject'] = 'test測試' # 郵件標題
                msg['From'] = 'AI Lab'  # 暱稱 或是 email
                msg['To'] = 'weiwen@alum.ccu.edu.tw'    # 收件人 email 或 暱稱
                msg['Cc'] = 'weiwen@alum.ccu.edu.tw, XXX@gmail.com'   # 副本收件人 email 
                msg['Bcc'] = 'weiwen@alum.ccu.edu.tw, XXX@gmail.com'  # 密件副本收件人 email

                status = email.sendMessage(msg.as_string())
                
                if status == {}:
                    print("Email sent successfully!")
                else:
                    print('Email send failed!')
            ```

        Reference
        ---------
        https://steam.oxxostudio.tw/category/python/example/gmail.html
        """
        super().__init__("smtp.gmail.com", 587)
        self.starttls()
        self.login(from_addr_pwd[0], from_addr_pwd[1])
        
        self.to_addr = to_addr
        self.from_addr = from_addr_pwd[0]
    
    def getText(self, message):
        return MIMEText(message)
                        
    def sendMessage(self, message):
        return self.sendmail(self.from_addr, self.to_addr, message)

    def __enter__(self) -> Self:
        return self
    
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, tb) -> None:
        self.quit()

class login_required_role:
    role:int = None
    message:str = None

    def __init__(self, role:int = -1, check_key:str = None, check_fn:Callable[[Any], None] = None):
        self.role = role
        self.check_key = check_key
        self.check_fn = check_fn
        self.message = self._get_message(role)

    def __call__(self, func:Callable):
        @wraps(func)
        def wrap(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            elif self.check_key:
                check_fn = self.check_fn or self._check_user_id
                check_fn(kwargs[self.check_key])
                return _login_required(func)(*args, **kwargs)
            elif current_user.rolenum > self.role:  
                abort(403, response=self.message)
            else:
                return _login_required(func)(*args, **kwargs)

        return wrap
    
    @classmethod
    def developer(cls, func:Callable):
        return cls(0)(func)

    @classmethod
    def admin(cls, func:Callable):
        return cls(1)(func)

    @classmethod
    def user(cls, func:Callable):
        return cls(2)(func)
    @classmethod
    def viewer(cls, func:Callable):
        return cls(3)(func)

    @classmethod
    def onlyself(cls, user_id):
        return cls()._check_user_id(user_id)
    
    def _get_message(self, role:int):
        _ = {
            -1: "不要亂看別人的資料喔~",
            0:"此功能僅提供給開發者使用",
            1:"此功能僅提供給管理員使用",
            2:"此功能僅提供給一般使用者與管理員使用",
            3:"此功能僅提供給登入者使用"
        }
        return _[role]
    
    def _check_user_id(self, user_id:int):
        if current_user.get_id() != str(user_id) and current_user.rolenum > 0:
            abort(403, response=self.message)
    
if __name__ == "__main__":
    print(get_ssh_key())