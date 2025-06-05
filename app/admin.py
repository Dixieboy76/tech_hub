from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, current_app
from wtforms.fields import PasswordField
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from .utils.email import send_verification_email

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))

def generate_email_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification-salt')

def init_admin(app):
    from .extensions import db
    from .models import User, Job
    from .utils.email import send_verification_email
    
    class UserAdminView(SecureModelView):
        column_list = ['username', 'email', 'is_tech', 'is_admin', 'email_verified', 'created_at']
        column_searchable_list = ['username', 'email']
        column_filters = ['is_tech', 'is_admin', 'email_verified', 'created_at']
        form_columns = ['username', 'email', 'password', 'is_tech', 'is_admin']
        form_extra_fields = {
            'password': PasswordField('New Password')
        }
        
        def on_model_change(self, form, model, is_created):
            if form.password.data:
                model.password = form.password.data
            if is_created:
                model.verification_token = generate_email_token(model.email)
                model.email_verified = False
                try:
                    send_verification_email(model)
                except Exception as e:
                    current_app.logger.error(f"Failed to send verification email: {e}")

    class JobAdminView(SecureModelView):
        column_list = ['title', 'status', 'customer_name', 'location', 'created_at', 'technician']
        column_searchable_list = ['title', 'description', 'customer_name']
        column_filters = ['status', 'created_at', 'tech_id']
        form_columns = ['title', 'description', 'status', 'location', 
                      'customer_name', 'customer_contact', 'tech_id']
        column_formatters = {
            'technician': lambda v, c, m, p: m.technician.username if m.technician else None
        }

    # Initialize admin interface once
    admin = Admin(app, 
                name='Tech Hub Admin', 
                template_mode='bootstrap3',
                base_template='admin/master.html')
    
    # Add views
    admin.add_view(UserAdminView(User, db.session, name='Users', category='Management'))
    admin.add_view(JobAdminView(Job, db.session, name='Jobs', category='Management'))