from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for
from wtforms.fields import PasswordField

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))

def init_admin(app):
    from .extensions import db
    from .models import User, Job
    
    class UserAdminView(SecureModelView):
        column_list = ['username', 'email', 'is_tech', 'is_admin', 'created_at']
        column_exclude_list = ['password_hash']
        form_columns = ['username', 'email', 'is_tech', 'is_admin']
        form_extra_fields = {
            'new_password': PasswordField('New Password')
        }
        
        def on_model_change(self, form, model, is_created):
            if form.new_password.data:
                model.password = form.new_password.data

    class JobAdminView(SecureModelView):
        column_searchable_list = ['title', 'description', 'customer_name']
        column_filters = ['status', 'created_at']
        form_columns = ['title', 'description', 'status', 'location', 
                       'customer_name', 'customer_contact', 'tech_id']

    admin = Admin(app, name='Tech Hub Admin', template_mode='bootstrap3')
    admin.add_view(UserAdminView(User, db.session, name='Users', category='Management'))
    admin.add_view(JobAdminView(Job, db.session, name='Jobs', category='Management'))