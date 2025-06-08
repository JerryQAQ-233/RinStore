from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .data_manager import DataManager

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError

auth_bp = Blueprint('auth', __name__)
data_manager = DataManager()

# Form Classes
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.get(username.data)
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

class ForgotPasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()]) # In a real app, EmailField(validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.get(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('routes.index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('main/auth-login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # Username validation (checking if exists) is done by form.validate_username

        hashed_password = generate_password_hash(password)
        User.create_user(username, hashed_password)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('main/auth-register.html', form=form)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        username = form.username.data
        # In a real application, you would use the username (or email)
        # to find the user and initiate a password reset email.
        flash('If an account with that username exists, a password reset link has been sent to the associated email.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('main/auth-forgot-password.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))