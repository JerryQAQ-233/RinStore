import json
import os
from datetime import datetime
import requests

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
        self.product_prices_file = os.path.join(self.data_dir, 'product_prices.json')
        
        # Initialize all data files
        self.get_unpaid_orders()
        self.get_recharge_history()
        self.get_redeem_codes()
        self.get_users()
        self.get_product_prices()

    def _load_data(self, filepath):
        vec_secret = os.getenv('VEC_SECRET')
        if vec_secret:
            # Determine the key name based on the filepath
            file_basename = os.path.basename(filepath)
            # Remove .json extension to get the key name
            key_name = os.path.splitext(file_basename)[0]
            
            # Construct the Edge Config URL
            # Assuming the Edge Config ID is also available as an environment variable or hardcoded if it's constant
            # For this example, let's assume the Edge Config ID is part of VEC_SECRET or another env var
            # For simplicity, let's assume VEC_SECRET is the full connection string for now
            # In a real scenario, you'd use the @vercel/edge-config SDK or parse the connection string
            
            # For direct HTTP request, we need the Edge Config ID and a read access token.
            # Let's assume VEC_SECRET is the read access token and EDGE_CONFIG_ID is another env var.
            edge_config_id = os.getenv('EDGE_CONFIG_ID')
            if not edge_config_id:
                print("Error: EDGE_CONFIG_ID environment variable not set for Edge Config.")
                return {}

            edge_config_url = f"https://edge-config.vercel.com/{edge_config_id}/item/{key_name}"
            headers = {"Authorization": f"Bearer {vec_secret}"}
            
            try:
                response = requests.get(edge_config_url, headers=headers)
                response.raise_for_status() # Raise an exception for HTTP errors
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching from Edge Config for {key_name}: {e}")
                return {}
        else:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    try:
                        return json.load(f)
                    except json.JSONDecodeError:
                        return {}
        return {}

    def _save_data(self, filepath, data):
        vec_secret = os.getenv('VEC_SECRET')
        if not vec_secret: # Only save to local file if VEC_SECRET is not set
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
        # If VEC_SECRET is set, _load_data will handle fetching from Edge Config
        # Otherwise, it will load from local file
        codes = self._load_data(self.redeem_codes_file)
        if not codes:
            self._save_data(self.redeem_codes_file, default_codes)
            return default_codes
        return codes

    def save_redeem_codes(self, codes):
        self._save_data(self.redeem_codes_file, codes)

    def add_recharge_history(self, user_id, order_id, amount):
        """添加充值历史记录的通用函数"""
        recharge_history = self.get_recharge_history()
        recharge_history.append({
            'user_id': user_id,
            'order_id': order_id,
            'amount': amount,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self.save_recharge_history(recharge_history)

    def del_recharge_history(self, order_id):
        """删除充值历史记录的通用函数"""
        recharge_history = self.get_recharge_history()
        recharge_history = [item for item in recharge_history if item.get('order_id') != order_id]
        self.save_recharge_history(recharge_history)
    def get_users(self):
        return self._load_data(self.users_file)

    def save_users(self, users):
        self._save_data(self.users_file, users)

    def update_user_balance(self, user_id, amount):
        users = self.get_users()
        if user_id in users:
            users[user_id]['balance'] = float(users[user_id].get('balance', 0)) + amount
            self.save_users(users)
            return True
        return False

    def get_product_prices(self):
        default_prices = {
            1: 10.00,
            2: 20.00
        }
        # If VEC_SECRET is set, _load_data will handle fetching from Edge Config
        # Otherwise, it will load from local file
        prices = self._load_data(self.product_prices_file)
        if not prices:
            self._save_data(self.product_prices_file, default_prices)
            return default_prices
        # Ensure keys are integers
        return {int(k): v for k, v in prices.items()}

    def save_product_prices(self, prices):
        self._save_data(self.product_prices_file, prices)


global_app = DataManager()