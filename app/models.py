from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .data_manager import DataManager

data_manager = DataManager()

class User(UserMixin):
    def __init__(self, id, password_hash):
        self.id = id
        self.password_hash = password_hash

    @staticmethod
    def get(user_id):
        users = data_manager.get_users()
        for user_data in users:
            if user_data['id'] == user_id:
                return User(user_data['id'], user_data['password_hash'])
        return None

    @staticmethod
    def create_user(user_id, password_hash):
        users = data_manager.get_users()
        users.append({'id': user_id, 'password_hash': password_hash})
        data_manager.save_users(users)