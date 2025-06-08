from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User

auth_bp = Blueprint('auth', __name__)

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

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))