"""
Key Points:
Password Handling:

password property setter automatically hashes passwords

Both check_password() and verify_password() work

Never stores plain text passwords

Security:

Uses Werkzeug's secure password hashing

Proper user authentication flow

Admin protection through is_admin flag

Consistency:

All password-related methods are properly implemented

The login route uses check_password()

Alternative verify_password() available if needed

"""



from flask import Flask
from .extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Setup login manager
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Initialize admin
    with app.app_context():
        from .admin import init_admin
        init_admin(app)
    
    # Register blueprints
    from .routes import main_routes, auth_routes
    app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes)
    
    return app