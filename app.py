from flask import Flask, render_template, request, redirect, url_for, session
import uuid
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify, request
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

app = Flask(__name__)
app.secret_key = 'your_secret_key' # Replace with a strong secret key

unpaid_orders = [] # Global list to store unpaid orders
recharge_history = [] # Global list to store recharge history

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 在实际应用中，密码应该从数据库中获取，并且是哈希过的
        # 这里为了演示，我们直接使用一个硬编码的哈希密码
        hashed_password = generate_password_hash('test123') # 'password' 是明文密码，实际应用中不应这样硬编码

        if username == 'test' and check_password_hash(hashed_password, password):
            user = User(id=username) # 使用用户名作为用户ID
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('main/auth-login.html', error='Invalid credentials')
    return render_template('main/auth-login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('main/index.html')

@app.route('/products')
@login_required
def products():
    return render_template('main/products.html')

@app.route('/wallet')
@login_required
def wallet():
    return render_template('main/wallet.html', recharge_history=recharge_history)

@app.route('/order', methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    order_type = data.get('type') # 'product' or 'recharge'

    order_id = str(uuid.uuid4())
    confirmation_id = str(uuid.uuid4())
    
    if order_type == 'product':
        plan_id = data.get('plan_id')
        amount = 10.00 if plan_id == 1 else 20.00 # Example amount based on plan_id
        order_info = {'order_id': order_id, 'confirmation_id': confirmation_id, 'plan_id': plan_id, 'amount': amount, 'status': 'unpaid', 'type': 'product'}
        unpaid_orders.append(order_info)
        print(f"Unpaid product order created: {order_id} with confirmation ID {confirmation_id}")
        return jsonify({'success': True, 'redirect_url': url_for('payment', order_id=order_id, confirmation_id=confirmation_id, _external=True)})
    elif order_type == 'recharge':
        amount = data.get('amount')
        if amount and amount > 0:
            order_info = {'order_id': order_id, 'confirmation_id': confirmation_id, 'plan_id': 0, 'amount': amount, 'status': 'unpaid', 'type': 'recharge'}
            unpaid_orders.append(order_info)
            recharge_history.append({'order_id': order_id, 'amount': amount, 'status': 'unpaid', 'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            print(f"Unpaid recharge order created: {order_id} with confirmation ID {confirmation_id}")
            return jsonify({'success': True, 'message': 'Recharge successful!', 'redirect_url': url_for('payment', order_id=order_id, confirmation_id=confirmation_id, _external=True)})
        return jsonify({'success': False, 'message': 'Invalid amount.'}), 400
    
    return jsonify({'success': False, 'message': 'Invalid order type.'}), 400

@app.route('/payment')
def payment():
    order_id = request.args.get('order_id')
    confirmation_id = request.args.get('confirmation_id')

    target_order = None
    if order_id and confirmation_id:
        for order in unpaid_orders:
            if order['order_id'] == order_id and order['confirmation_id'] == confirmation_id:
                target_order = order
                break

    if target_order:
        return render_template('main/payment.html', order_id=target_order['order_id'], amount=target_order['amount'])
    elif unpaid_orders:
        latest_order = unpaid_orders[-1]  # Fallback to latest unpaid order if no specific order found
        return render_template('main/payment.html', order_id=latest_order['order_id'], amount=latest_order['amount'])
    
    return render_template('main/payment.html', order_id='N/A', amount='N/A')

@app.route('/callback', methods=['GET', 'POST'])
@login_required
def payment_callback():
    # This is where your payment gateway would send a callback
    # You would verify the payment and update the user's balance
    # For demonstration, we'll just simulate a successful payment.
    data = request.get_json()
    status = data.get('status')
    confirmation_id = data.get('confirmation_id') # Get confirmation ID from callback

    if status == 'success' and confirmation_id:
        for order in unpaid_orders:
            if order['confirmation_id'] == confirmation_id:
                order['status'] = 'paid'
                # Here you would typically update your database with the paid order
                # For now, let's just print it
                print(f"Order {order['order_id']} with confirmation ID {confirmation_id} paid successfully!")
                recharge_history.append({'order_id': order['order_id'], 'amount': order['amount'], 'status': 'paid', 'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                unpaid_orders.remove(order) # Remove the paid order from the list
                return jsonify({'message': 'Payment successful and balance topped up!'})
        return jsonify({'message': 'Order not found or already paid.'}, 404)
    return jsonify({'message': 'Invalid callback data.'}, 400)

@app.route('/redeem', methods=['POST'])
@login_required
def redeem_code():
    data = request.get_json()
    code = data.get('code')

    # For demonstration purposes, let's assume a simple valid code and amount
    if code == 'MYREDEEMCODE123':
        redeem_amount = 50.00
        # In a real application, you would:
        # 1. Check if the code is valid and hasn't been used.
        # 2. Mark the code as used.
        # 3. Update the user's balance in the database.
        # 4. Log the redemption.
        print(f"User {current_user.id} redeemed code {code} for {redeem_amount}")
        # Simulate adding to recharge history for display purposes
        recharge_history.append({'order_id': f'REDEEM-{code}', 'amount': redeem_amount, 'status': 'redeemed', 'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        return jsonify({'success': True, 'message': f'Successfully redeemed {redeem_amount}!'})
    else:
        return jsonify({'success': False, 'message': 'Invalid or expired redemption code.'}), 400

if __name__ == '__main__':
    app.run(debug=True)


