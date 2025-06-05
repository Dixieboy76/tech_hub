from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user, login_user, logout_user
from app.models import Job, User
from app.forms import JobForm, RegistrationForm, LoginForm, ResetPasswordRequestForm, ResetPasswordForm
from app import db, login_manager
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from app.utils.email import send_password_reset_email, send_verification_email

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
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

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
        user.password = form.password.data
        user.verification_token = generate_email_token(user.email)
        db.session.add(user)
        db.session.commit()
        
        send_verification_email(user)
        flash('Registration successful! Please check your email to verify your account.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_routes.route('/verify_email/<token>')
def verify_email(token):
    if current_user.is_authenticated and current_user.email_verified:
        return redirect(url_for('main.index'))
    
    email = verify_email_token(token)
    if not email:
        flash('Invalid or expired verification link.', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first_or_404()
    if user.email_verified:
        flash('Account already verified.', 'info')
    else:
        user.email_verified = True
        user.verification_token = None
        db.session.commit()
        flash('Thank you for verifying your email address!', 'success')
    
    return redirect(url_for('main.index'))

@auth_routes.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_reset_token(user.email)
            user.reset_token = token
            user.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            send_password_reset_email(user)
        flash('If your email is registered, you will receive instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', form=form)

@auth_routes.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    email = verify_reset_token(token)
    if not email:
        flash('Invalid or expired password reset link.', 'danger')
        return redirect(url_for('auth.reset_password_request'))
    
    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()
        flash('Your password has been reset. You can now login with your new password.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth_routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

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

# Main Routes
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
    
    if not current_user.check_password(current_password):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('main.profile'))
    
    current_user.username = request.form.get('username')
    current_user.email = request.form.get('email')
    
    if new_password:
        current_user.password = new_password
    
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('main.profile'))

# Token Generation/Verification
def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, max_age=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=max_age
        )
    except:
        return None
    return email

def generate_email_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification-salt')

def verify_email_token(token, max_age=86400):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='email-verification-salt',
            max_age=max_age
        )
    except:
        return None
    return email

def init_app(app):
    app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes)