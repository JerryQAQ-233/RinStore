from flask import render_template, redirect, url_for, request, jsonify, current_app as app
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required
from .data_manager import get_recharge_history # Import get_recharge_history from data_manager.py

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
@login_required
def index():
    return render_template('main/index.html')

@routes_bp.route('/products')
@login_required
def products():
    return render_template('main/products.html')

@routes_bp.route('/wallet')
@login_required
def wallet():
    recharge_history = get_recharge_history()
    return render_template('main/wallet.html', recharge_history=recharge_history)