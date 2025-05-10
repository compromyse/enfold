from flask_login import UserMixin
from tinydb import TinyDB, Query

db = TinyDB('db.json')
users_table = db.table('users')
UserQuery = Query()

class User(UserMixin):
    def __init__(self, username, admin):
        self.id = username
        self.admin = admin

    @staticmethod
    def get(username):
        result = users_table.get(UserQuery.username == username)
        if result:
            return User(username, result['admin'])
        return None

    @staticmethod
    def validate_login(username, password):
        user = users_table.get((UserQuery.username == username) & (UserQuery.password == password))
        if user:
            return User(username, user['admin'])

        return None

    @staticmethod
    def create(username, password, admin=False):
        if users_table.get(UserQuery.username == username):
            return None

        users_table.insert({'username': username, 'password': password, 'admin': admin})
        return User(username, admin)

User.create('admin', 'dontguessthisplzahh', admin=True)
