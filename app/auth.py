from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .data_manager import DataManager

auth_bp = Blueprint('auth', __name__)
data_manager = DataManager()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.get(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('routes.index'))
        else:
            # For demonstration, if user doesn't exist, create a new one with the provided credentials
            # In a real application, you would have a registration process
            if not user:
                hashed_password = generate_password_hash(password)
                User.create_user(username, hashed_password)
                user = User.get(username)
                login_user(user)
                return redirect(url_for('routes.index'))
            return render_template('main/auth-login.html', error='Invalid credentials')
    return render_template('main/auth-login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('main/auth-register.html', error='Passwords do not match')

        user = User.get(username)
        if user:
            return render_template('main/auth-register.html', error='Username already exists')
        
        hashed_password = generate_password_hash(password)
        User.create_user(username, hashed_password)
        user = User.get(username)
        login_user(user)
        return redirect(url_for('routes.index'))
    return render_template('main/auth-register.html')

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        if new_password != confirm_new_password:
            return render_template('main/auth-forgot-password.html', error='Passwords do not match')

        user = User.get(username)
        if not user:
            return render_template('main/auth-forgot-password.html', error='User not found')

        hashed_password = generate_password_hash(new_password)
        User.update_password(username, hashed_password)
        return redirect(url_for('auth.login'))
    return render_template('main/auth-forgot-password.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))