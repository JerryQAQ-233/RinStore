import json
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        
        # Ensure the data directory exists
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.unpaid_orders_file = os.path.join(self.data_dir, 'unpaid_orders.json')
        self.recharge_history_file = os.path.join(self.data_dir, 'recharge_history.json')
        self.redeem_codes_file = os.path.join(self.data_dir, 'redeem_codes.json')
        self.users_file = os.path.join(self.data_dir, 'users.json')
        
        # Initialize all data files
        self.get_unpaid_orders()
        self.get_recharge_history()
        self.get_redeem_codes()
        self.get_users()

    def _load_data(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def _save_data(self, filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def get_unpaid_orders(self):
        return self._load_data(self.unpaid_orders_file)

    def save_unpaid_orders(self, orders):
        self._save_data(self.unpaid_orders_file, orders)

    def get_recharge_history(self):
        return self._load_data(self.recharge_history_file)

    def save_recharge_history(self, history):
        self._save_data(self.recharge_history_file, history)

    def get_redeem_codes(self):
        default_codes = []
        codes = self._load_data(self.redeem_codes_file)
        if not codes:
            self._save_data(self.redeem_codes_file, default_codes)
            return default_codes
        return codes

    def save_redeem_codes(self, codes):
        self._save_data(self.redeem_codes_file, codes)

    def add_recharge_history(self, order_id, amount, status):
        """添加充值历史记录的通用函数"""
        recharge_history = self.get_recharge_history()
        recharge_history.append({
            'order_id': order_id,
            'amount': amount,
            'status': status,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self.save_recharge_history(recharge_history)

    def get_users(self):
        return self._load_data(self.users_file)

    def save_users(self, users):
        self._save_data(self.users_file, users)


global_app = DataManager()