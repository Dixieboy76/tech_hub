from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user, login_user, logout_user
from app.models import Job, User
from app.forms import JobForm, RegistrationForm, LoginForm
from app import db, login_manager


# Create Blueprints
main_routes = Blueprint('main', __name__)
auth_routes = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/admin'):
        flash('Please login as admin to access this page', 'warning')
        return redirect(url_for('auth.login'))
    flash('Please login to access this page', 'warning')
    return redirect(url_for('auth.login'))

# Auth Routes
@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):  # Now using check_password
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.dashboard'))
        flash('Login failed. Check your email and password.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_tech=form.is_tech.data
        )
        user.password = form.password.data  # This will automatically hash the password
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_routes.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    # Implement password reset logic
    pass


@main_routes.route('/')
def index():
    return render_template('index.html')


@main_routes.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_tech:
        jobs = Job.query.filter_by(tech_id=current_user.id).all()
    else:
        jobs = Job.query.all()
    return render_template('dashboard.html', jobs=jobs)


@main_routes.route('/jobs', methods=['GET', 'POST'])
@login_required
def jobs():
    form = JobForm()
    
    # Handle job creation
    if form.validate_on_submit():
        job = Job(
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            tech_id=current_user.id if current_user.is_tech else None,
            customer_name=form.customer_name.data,
            customer_contact=form.customer_contact.data,
            status='Pending'
        )
        db.session.add(job)
        db.session.commit()
        flash('Job created successfully!', 'success')
        return redirect(url_for('main.jobs'))
    
    # Get jobs based on user type
    if current_user.is_tech:
        jobs = Job.query.filter_by(tech_id=current_user.id).order_by(Job.created_at.desc()).all()
    else:
        jobs = Job.query.order_by(Job.created_at.desc()).all()
    
    return render_template('jobs.html', form=form, jobs=jobs)


@main_routes.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main_routes.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    
    # Verify current password
    if not current_user.check_password(current_password):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('main.profile'))
    
    # Update username and email
    current_user.username = request.form.get('username')
    current_user.email = request.form.get('email')
    
    # Update password if new one provided
    if new_password:
        current_user.password = new_password  # Automatically hashes
    
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('main.profile'))

@auth_routes.route('/promote/<int:user_id>')
@login_required
def promote_to_admin(user_id):
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f'{user.username} has been promoted to admin', 'success')
    return redirect(url_for('admin.index'))




def init_app(app):
    """Initialize routes with the app"""
    app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes)