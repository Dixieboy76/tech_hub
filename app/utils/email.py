from flask import render_template, current_app
from flask_mail import Message
from app.extensions import mail

def send_password_reset_email(user):
    with current_app.app_context():
        token = user.reset_token
        msg = Message('Password Reset Request',
                    sender=current_app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[user.email])
        msg.body = render_template('email/reset_password.txt', 
                                 user=user, token=token)
        msg.html = render_template('email/reset_password.html', 
                                 user=user, token=token)
        mail.send(msg)

def send_verification_email(user):
    with current_app.app_context():
        token = user.verification_token
        msg = Message('Verify Your Email',
                    sender=current_app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[user.email])
        msg.body = render_template('email/verify_email.txt', 
                                 user=user, token=token)
        msg.html = render_template('email/verify_email.html', 
                                 user=user, token=token)
        mail.send(msg)