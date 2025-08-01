from utils.model import db, User, Setting, Container

from flask import Flask
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin

class IndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin.html')

class DebugContainerView(ModelView):
    form_columns = ['container_id', 'name', 'password', 'user_id']  # ✅ 強制加入 user 欄位
    def create_form(self, obj=None):
        form = super().create_form(obj)
        print("🧪 表單欄位:", [f.name for f in form])
        return form

def initAdmin(app:Flask):
    ###* Index View ###
    admin = Admin(app, name=app.config['TITLE'], template_mode='bootstrap3') # , index_view=IndexView()

    ###* File View ###
    admin.add_view(FileAdmin('/', name='File Manager', endpoint='/file_manager'))

    ###* Model View ###
    admin.add_view(ModelView(User, db.session, 'User Manager', endpoint='/user', category="DataBase"))
    admin.add_view(ModelView(Setting, db.session, 'Setting Manager', endpoint='/setting', category="DataBase"))
    admin.add_view(DebugContainerView(Container, db.session, 'Container Manager', endpoint='/container', category="DataBase"))
    return admin
