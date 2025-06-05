from flask import Flask
from .extensions import db, login_manager, mail

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)  # Initialize Flask-Mail
    
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