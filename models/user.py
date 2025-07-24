from utils.db import get_collection
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, username, password_hash, email, balance=0.0, role='customer'):
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.balance = balance
        self.role = role

    @staticmethod
    def find_by_username(username):
        users = get_collection('users')
        data = users.find_one({'username': username})
        if data:
            return User(data['username'], data['password_hash'], data['email'], data.get('balance', 0.0), data.get('role', 'customer'))
        return None

    @staticmethod
    def create(username, password, email, role='customer'):
        users = get_collection('users')
        if users.find_one({'username': username}) or users.find_one({'email': email}):
            return None
        password_hash = generate_password_hash(password)
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'balance': 0.0,
            'role': role
        }
        users.insert_one(user_data)
        return User(username, password_hash, email, 0.0, role)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save_balance(self):
        users = get_collection('users')
        users.update_one({'username': self.username}, {'$set': {'balance': self.balance}})

    @staticmethod
    def all_customers():
        users = get_collection('users')
        return list(users.find({'role': 'customer'}, {'password_hash':0}))

