from application import *
from utils.utils import *

from application.model import db, User as UserDB, Setting, Container
from flask import Flask
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from wtforms import SelectField
from utils.g import current_user

def check_permissions():
    if current_user.is_authenticated and current_user.rolenum <= 1:
        pass
    else:
        abort(401, response = login_required_role(1).message)

class IndexView(AdminIndexView):
    @expose('/')
    def index(self):
        check_permissions()
        #TODO 
        string = [
            "管理員注意事項",
            "1. 對 DGX 的任何操作先優先使用此系統, 若此系統沒有再對 DGX 下指令.",
            "2. 因任何原因 (如: 停電) 需要將DGX關機時, 請先使用 Other/Broadcast 功能通知所有人."
        ]
        return self.render("admin/index.html", admin_notice = "<br>".join(string))


    @expose('/broadcast', methods=['GET', 'POST'])
    def broadcast(self,  **kwargs):
        check_permissions()
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


class AuthModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.rolenum <= 1

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')
    
class UserView(AuthModelView):
    form_overrides = {
        'role': SelectField
    }
    form_args = {
        'role': {
            'choices': [
                ('developer', 'Developer'), # (值, 顯示文字)
                ('admin', 'Admin'),
                ('user', 'User'),
                ('viewer', 'Viewer')
            ],
        }
    }
    def on_model_change(self, form, model:UserDB, is_created:bool):
        if is_created:
            # abort(400, response = "禁止直接從資料庫創建使用者")
            pass
        else:
            pass

        logger.debug(
            f"[Change User] {model.name}({model.username}) (is_created: {is_created})"
        )

    def on_model_delete(self, model:UserDB):
        # 檢查被刪除的模型是否為 UserDB 類型
        from shutil import rmtree
        if isinstance(model, UserDB):
            if model.role in ('admin', 'developer'):
                abort(400, response = f"不得刪除權限為 {model.role} 的資料")
            user_folder_path = Path(f'/home/lab120/user_data/{model.username}')
            if user_folder_path.exists():
                try:
                    rmtree(str(user_folder_path))
                    logger.info(f"Removed user folder for user: {model.username}")
                except OSError as e:
                    logger.error(f"Error removing user folder {user_folder_path}: {e}")
    
class AuthFileAdmin(FileAdmin):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.rolenum <= 1

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
    admin.add_view(UserView(UserDB, db.session, 'User Manager', endpoint='/user', category="DataBase"))
    admin.add_view(AuthModelView(Setting, db.session, 'Setting Manager', endpoint='/setting', category="DataBase"))
    admin.add_view(DebugContainerView(Container, db.session, 'Container Manager', endpoint='/container', category="DataBase"))

    admin.add_link(MenuLink(name='Broadcast', url='/admin/broadcast', category='Other'))

    return admin
