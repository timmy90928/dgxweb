from . import *

from utils.model import db, User as UserDB, Setting, Container
from flask import Flask
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from utils.g import current_user

class IndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.is_authenticated and current_user.rolenum < 1:
            #TODO 
            string = [
                "管理員注意事項",
                "1. 因任何原因 (如: 停電) 需要將DGX關機時, 請先使用 Other/Broadcast 功能通知所有人."
            ]
            return self.render("admin/index.html", admin_notice = "<br>".join(string))
        else:
            return redirect('/')
    
    @expose('/broadcast', methods=['GET', 'POST'])
    def broadcast(self,  **kwargs):
        if current_user.is_authenticated and current_user.rolenum < 1:
            all_users:list[UserDB] = UserDB.query.all()
            admin_user:UserDB = UserDB.query.filter_by(username='admin').first()
            if request.method == 'POST':
                from .api import send_email_in_background
                
                form = request.form
                send_email_in_background({
                        "Subject": form['subject'],# "[AILAB DGX] 廣播測試",
                        "From": "AILAB DGX TEAM",
                        "To": admin_user.email,
                        "Bcc": [user.email for user in all_users],
                        "Text": str(form['content']).split('\n')
                    })
                return redirect('/alert/已寄送, 請等待一下後, 到自己的信箱確認是否成功?to=/admin/broadcast')
            
            return self.render('admin/broadcast.html', all_users=all_users, admin_user=admin_user)
        
        else:
            return redirect('/')
    
class AuthModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.rolenum < 1

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')
    
class AuthFileAdmin(FileAdmin):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.rolenum < 1

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')

class DebugContainerView(AuthModelView):
    form_columns = ['container_id', 'name', 'password', 'user_id']
    column_list = ['container_id', 'name', 'password', 'user_id']


def initAdmin(app:Flask):
    ###* Index View ###
    admin = Admin(app, name=app.config['TITLE'], template_mode='bootstrap3', index_view=IndexView())

    ###* File View ###
    admin.add_view(AuthFileAdmin('/', name='File Manager', endpoint='/file_manager'))

    ###* Model View ###
    admin.add_view(AuthModelView(UserDB, db.session, 'User Manager', endpoint='/user', category="DataBase"))
    admin.add_view(AuthModelView(Setting, db.session, 'Setting Manager', endpoint='/setting', category="DataBase"))
    admin.add_view(DebugContainerView(Container, db.session, 'Container Manager', endpoint='/container', category="DataBase"))

    admin.add_link(MenuLink(name='Broadcast', url='/admin/broadcast', category="Other"))
    return admin
