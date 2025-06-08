from flask import Blueprint, request, jsonify, render_template, url_for
from flask_login import login_required, current_user

from .data_manager import get_unpaid_orders, save_unpaid_orders, add_recharge_history, get_redeem_codes, save_redeem_codes
from .order import OrderCreator

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/order', methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    order_creator = OrderCreator(data)
    return order_creator.process()

@payment_bp.route('/payment')
def payment():
    order_id = request.args.get('order_id')
    confirmation_id = request.args.get('confirmation_id')

    unpaid_orders = get_unpaid_orders()
    target_order = None
    
    if order_id and confirmation_id:
        target_order = next((order for order in unpaid_orders 
                           if order['order_id'] == order_id 
                           and order['confirmation_id'] == confirmation_id), None)

    if target_order:
        order_to_show = target_order
    elif unpaid_orders:
        order_to_show = unpaid_orders[-1]  # Fallback to latest unpaid order
    else:
        return render_template('main/payment.html', order_id='N/A', amount='N/A')
        
    return render_template('main/payment.html', 
                         order_id=order_to_show['order_id'], 
                         amount=order_to_show['amount'])

@payment_bp.route('/callback', methods=['GET', 'POST'])
@login_required
def payment_callback():
    data = request.get_json()
    status = data.get('status')
    confirmation_id = data.get('confirmation_id')

    if status == 'success' and confirmation_id:
        unpaid_orders = get_unpaid_orders()
        for order in unpaid_orders:
            if order['confirmation_id'] == confirmation_id:
                order['status'] = 'paid'
                print(f"Order {order['order_id']} with confirmation ID {confirmation_id} paid successfully!")
                add_recharge_history(order['order_id'], order['amount'], 'paid')
                unpaid_orders.remove(order)
                save_unpaid_orders(unpaid_orders)
                return jsonify({'message': 'Payment successful and balance topped up!'})
        return jsonify({'message': 'Order not found or already paid.'}, 404)
    return jsonify({'message': 'Invalid callback data.'}, 400)

@payment_bp.route('/redeem', methods=['POST'])
@login_required
def redeem_code():
    data = request.get_json()
    code = data.get('code')

    redeem_codes = get_redeem_codes()
    
    for redeem_code_obj in redeem_codes:
        if redeem_code_obj['code'] == code and not redeem_code_obj['used']:
            redeem_amount = redeem_code_obj['amount']
            redeem_code_obj['used'] = True
            save_redeem_codes(redeem_codes)
            print(f"User {current_user.id} redeemed code {code} for {redeem_amount}")
            add_recharge_history(f'REDEEM-{code}', redeem_amount, 'redeemed')
            return jsonify({'success': True, 'message': f'Successfully redeemed {redeem_amount}!'})
    
    return jsonify({'success': False, 'message': 'Invalid or expired redemption code.'}), 400
