from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Create extensions without initializing with app
db = SQLAlchemy()
login_manager = LoginManager()