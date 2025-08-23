
###* utils ###
from os import urandom
from utils.utils import errorCallback
from utils.utils import now_time
from utils.utils import get_ssh_key
from utils.utils import hash
from utils.g import rootdir
from application.model import _create_sqlite_uri

class Config:
    """General Settings."""
    ###* Basic ###
    TITLE = "AI LAB DGX"
    SERVER_RUN_TIME = now_time()
    SECRET_KEY = get_ssh_key()
    
    ###* JWT ###
    JWT_SECRET_KEY = urandom(32).hex()
    JWT_TOKEN_LOCATION = ["cookies"] # Tell Flask-JWT-Extended to expect the token in cookies
    
    ###* Database ###
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ###* Debug Or Testing ###
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development environment settings."""
    DEBUG = True
    PORT = 120
    # SQLALCHEMY_DATABASE_URI = _create_sqlite_uri(rootdir.joinpath('_test_dgx.db'))
    SQLALCHEMY_DATABASE_URI = _create_sqlite_uri(rootdir.joinpath('dgx.db'))


class ProductionConfig(Config):
    """Formal environment setting."""
    PORT = 80
    SQLALCHEMY_DATABASE_URI = _create_sqlite_uri(rootdir.joinpath('dgx.db'))
    
class TestingConfig(Config):
    """Test environment settings."""
    TESTING = True
    PORT = 120
    # 範例：測試環境使用一個獨立的資料庫
    # SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/prod_db'

# 建立一個字典，用於根據環境名稱獲取對應的配置類別
configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}