from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# Create extensions without initializing with app
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()