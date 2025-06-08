from flask import render_template, redirect, url_for, request
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required,current_user

from .data_manager import *
routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
@login_required
def index():
    user_balance = current_user.balance
    return render_template('main/index.html', user_balance=user_balance)

@routes_bp.route('/products')
@login_required
def products():
    return render_template('main/products.html')

@routes_bp.route('/wallet')
@login_required
def wallet():
    recharge_history = global_app.get_recharge_history()
    return render_template('main/wallet.html', recharge_history=recharge_history)

@routes_bp.route('/recharge', methods=['GET', 'POST'])
@login_required
def recharge():
    if request.method == 'POST':
        amount = float(request.form['amount'])

        order_id = f"recharge_{current_user.id}_{len(data_manager.get_recharge_history()) + 1}"
        data_manager.add_recharge_history(current_user.id, order_id, amount, 'success')
        flash(f'成功充值 {amount} 元！', 'success')
        return redirect(url_for('routes.recharge_history'))
    return render_template('main/recharge.html')

@routes_bp.route('/redeem', methods=['POST'])
@login_required
def redeem():
    if request.method == 'POST':
        code = request.form['code']
        redeem_codes = data_manager.get_redeem_codes()
        for rc in redeem_codes:
            if rc['code'] == code and not rc['used']:
                rc['used'] = True
                data_manager.save_redeem_codes(redeem_codes)
                flash(f'成功兑换 {rc["value"]} 元！', 'success')
                return redirect(url_for('routes.index'))
        flash('无效或已使用的兑换码！', 'danger')
        return redirect(url_for('routes.redeem'))