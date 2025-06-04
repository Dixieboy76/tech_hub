from app import create_app, db
from app.models import User, Job
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()

def initialize_database():
    with app.app_context():
        # Drop all existing tables (use with caution in production)
        db.drop_all()
        
        # Create all database tables
        db.create_all()
        
        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@techhub.com',
            password_hash=generate_password_hash('Admin@123'),  # Change this password!
            is_tech=True,
            is_admin=True,
            created_at=datetime.utcnow(),
            email_verified=True
        )
        
        # Create regular technician user
        technician = User(
            username='tech1',
            email='tech@techhub.com',
            password_hash=generate_password_hash('Tech@123'),
            is_tech=True,
            is_admin=False,
            created_at=datetime.utcnow(),
            email_verified=True
        )
        
        # Create regular customer user
        customer = User(
            username='customer1',
            email='customer@techhub.com',
            password_hash=generate_password_hash('Customer@123'),
            is_tech=False,
            is_admin=False,
            created_at=datetime.utcnow(),
            email_verified=True
        )
        
        # Add users to session
        db.session.add(admin_user)
        db.session.add(technician)
        db.session.add(customer)
        
        # Create sample jobs
        jobs = [
            Job(
                title='AC Repair',
                description='AC not cooling properly in living room',
                location='123 Main St, Anytown',
                status='Completed',
                created_at=datetime.utcnow(),
                tech_id=technician.id,
                customer_name='John Doe',
                customer_contact='555-0101'
            ),
            Job(
                title='Plumbing Leak',
                description='Kitchen sink leaking under cabinet',
                location='456 Oak Ave, Somewhere',
                status='In Progress',
                created_at=datetime.utcnow(),
                tech_id=technician.id,
                customer_name='Jane Smith',
                customer_contact='555-0202'
            ),
            Job(
                title='Electrical Inspection',
                description='Annual safety inspection required',
                location='789 Pine Rd, Nowhere',
                status='Pending',
                created_at=datetime.utcnow(),
                customer_name='Bob Johnson',
                customer_contact='555-0303'
            )
        ]
        
        # Add jobs to session
        for job in jobs:
            db.session.add(job)
        
        # Commit all changes
        db.session.commit()
        
        print("""
        Database initialized successfully!
        
        Sample users created:
        - Admin:      username='admin'      password='Admin@123'
        - Technician: username='tech1'      password='Tech@123'
        - Customer:   username='customer1'   password='Customer@123'
        """)

if __name__ == '__main__':
    initialize_database()


# python3 initialize_database.py --reset