'''神人gemini写的依托,等我想改的时候再改,反正能跑就行,对吧?'''
from datetime import datetime
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# Ensure the data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

UNPAID_ORDERS_FILE = os.path.join(DATA_DIR, 'unpaid_orders.json')
RECHARGE_HISTORY_FILE = os.path.join(DATA_DIR, 'recharge_history.json')
REDEEM_CODES_FILE = os.path.join(DATA_DIR, 'redeem_codes.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

def load_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def get_unpaid_orders():
    return load_data(UNPAID_ORDERS_FILE)

def save_unpaid_orders(orders):
    save_data(UNPAID_ORDERS_FILE, orders)

def get_recharge_history():
    return load_data(RECHARGE_HISTORY_FILE)

def save_recharge_history(history):
    save_data(RECHARGE_HISTORY_FILE, history)

def get_redeem_codes():
    # Example: Initial hardcoded redeem codes, will be loaded from JSON
    # In a real application, these would be managed via an admin interface
    default_codes = []
    codes = load_data(REDEEM_CODES_FILE)
    if not codes:
        save_data(REDEEM_CODES_FILE, default_codes)
        return default_codes
    return codes

def save_redeem_codes(codes):
    save_data(REDEEM_CODES_FILE, codes)

def add_recharge_history(order_id, amount, status):
    """添加充值历史记录的通用函数"""
    recharge_history = get_recharge_history()
    recharge_history.append({
        'order_id': order_id,
        'amount': amount,
        'status': status,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    save_recharge_history(recharge_history)

def get_users():
    return load_data(USERS_FILE)

def save_users(users):
    save_data(USERS_FILE, users)

# Initialize data files if they don't exist
get_unpaid_orders()
get_recharge_history()
get_redeem_codes()
get_users()