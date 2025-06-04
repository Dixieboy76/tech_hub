from app import create_app
from app.models import User
from app.extensions import db

app = create_app()

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='admin@example.com').first()
    
    if admin:
        print("Admin user already exists:")
        print(f"ID: {admin.id}")
        print(f"Username: {admin.username}")
        print(f"Is Admin: {admin.is_admin}")
    else:
        # Create new admin
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.password = 'adminpassword'  # Change to a secure password
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully")