# https://blog.csdn.net/qq_42265220/article/details/120670267
# https://www.maxlist.xyz/2019/10/30/flask-sqlalchemy/
#? strftime('%Y-%m-%d', timestamp, 'unixepoch','localtime')

from flask import Flask, current_app
from utils.utils import timestamp as _timestamp, now_time
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, model
from sqlalchemy import Column as SAColumn, Integer, String, Date, Float, ForeignKey, Text, desc
from utils.utils import hash
from typing import Union, Literal

VERSION = '1'

class SQLAlchemy(_SQLAlchemy):

    # __table_args__ = {'extend_existing': True}
    # __tablename__ = ''
    Integer = Integer
    String = String
    Date = Date
    Float = Float
    Text = Text
    ForeignKey = ForeignKey
    """
    一對多的多
    """

    def __init__(self, app:Flask  = None):
        """
        Initialize an instance of SQLAlchemy.

        ```
        db = SQLAlchemy()
        db.add()
        db.session.delete()
        ```
        """
        super().__init__(app)
    
    def __call__(self, sql:str):
        """
        >>> db = SQLAlchemy()
        >>> result = db('select * from account')
        """
        return self.session.execute(sql)
    
    def Column(
        self, 
        _type, 
        *args,
        nullable=True, 
        primary_key=False, 
        autoincrement=False, 
        unique=False, 
        default=None, 
        name=None, 
        **kwargs
    ):
        
        return SAColumn(
            _type, 
            *args, 
            nullable=nullable, 
            primary_key=primary_key, 
            autoincrement=autoincrement, 
            unique=unique, 
            default=default,
            name=name, 
            **kwargs 
        )
    
    def relationship_backref(self, argument, backref=None, back_populates=None, *, secondary=None, lazy:Literal['select', 'dynamic']="select", foreign_keys=None, **kwargs):
        """
        一對多的一

        :param argument: 一對多的多, class name
        :param backref: 一對多的多 對 一對多的一 的 新名稱

        ```
        class User(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(64), unique=True, index=True)
            posts = db.relationship_backref('Post', backref='author', lazy='dynamic')
        
        class Post(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            title = db.Column(db.String(128))
            body = db.Column(db.Text)
            user_id = db.Column(db.Integer, foreignKey = db.ForeignKey('user.id'))
        
        # 查詢使用者
        user = User.query.filter_by(username='john').first()

        # 訪問使用者的所有文章
        for post in user.posts:
            print(post.title)

        # 查詢文章
        post = Post.query.first()

        # 訪問文章的作者
        print(post.author.username)
        ```
        """
        return self.relationship(
            argument,
            secondary=secondary,
            backref=backref,
            back_populates=back_populates,
            uselist=True,
            lazy=lazy,
            cascade=None,
            passive_deletes=False,
            foreign_keys=foreign_keys,
            primaryjoin=None,
            secondaryjoin=None,
            order_by=None,
            single_parent=False,
            viewonly=False,
            enable_typechecks=True,
            join_depth=None,
            comparator_factory=None,
            info=None,
            overlaps=None
        )
    
    @property
    def pk(self):
        """```
        >>> db.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
        ```"""
        return self.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
    
    def delete(self, instance:model.Model, commit:bool = True):
        # assert self.Model in instance, 'Model not found.'
        self.session.delete(instance)
        if commit: self.commit()

    def add(self, instance:model.Model, commit:bool = True):
        # assert self.Model in instance, 'Model not found.'
        self.session.add(instance)
        if commit: self.commit()

    def commit(self) -> None:
        self.session.commit()
    
    def close(self) -> None:
        self.session.close()


db = SQLAlchemy()

def _create_sqlite_uri(abspath) -> str:
    return 'sqlite:///' + str(abspath)

class User(db.Model):
    id = db.pk
    username = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text)
    password = db.Column(db.Text)
    email = db.Column(db.Text)
    role = db.Column(db.Text,nullable=False,  default='user')
    container = db.relationship_backref('Container', backref='user')

    def __init__(self, username, email, password, name, role):
        self.username = username
        self.password = hash(password)
        self.name = name
        self.email = email
        self.role = role

    def check_password(self, password):
        """
        ```
        user = User.query.filter_by(username="john_doe").first()
        if user.check_password("securepassword"):
            print("Password is correct")
        ```
        """
        return hash(password) == self.password

    def __str__(self):
        return '<User %r>' % self.username

class Container(db.Model):
    id = db.pk
    container_id = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, container_id, name, password, user_id):
        self.container_id = container_id
        self.name = name
        self.password = password
        self.user_id = user_id

    @property
    def container(self):
        from utils.dockers import Container as docker_container
        return docker_container(self.container_id)


class Setting(db.Model):
    __tablename__ = 'Setting'
    id = db.pk
    key = db.Column(db.Text, nullable=False, unique=True)
    value = db.Column(db.Text)

    @classmethod
    def get(cls, key, default = None) -> str:
        _setting:Setting = cls.query.filter_by(key=key).first()
        if _setting:
            return _setting.value
        else:
            db.add(cls(key, default))
            cls.get(key, default)
    @classmethod
    def set(cls, key, value):
        _setting:Setting = cls.query.filter_by(key=key).first()
        if _setting:
            _setting.value = value
            db.commit()
        else:
            db.add(cls(key, value))
        
    def __init__(self, key, value):
        self.key = key
        self.value = value
