from flask_login import UserMixin

from .data_manager import get_users, save_users

class User(UserMixin):
    def __init__(self, id, password_hash):
        self.id = id
        self.password_hash = password_hash

    @staticmethod
    def get(user_id):
        users = get_users()
        for user_data in users:
            if user_data['id'] == user_id:
                return User(user_data['id'], user_data['password_hash'])
        return None

    @staticmethod
    def create_user(user_id, password_hash):
        users = get_users()
        users.append({'id': user_id, 'password_hash': password_hash})
        save_users(users)