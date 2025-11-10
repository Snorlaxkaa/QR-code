from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        # 這裡可以改用資料庫查詢
        users = {
            1: {"username": "admin", "password": "0000"}  # 預設管理員帳號
        }
        user_data = users.get(int(user_id))
        if not user_data:
            return None
        return User(int(user_id), user_data["username"], user_data["password"])

    @staticmethod
    def get_by_username(username):
        # 這裡可以改用資料庫查詢
        users = {
            "admin": {"id": 1, "password": "0000"}  # 預設管理員帳號
        }
        user_data = users.get(username)
        if not user_data:
            return None
        return User(user_data["id"], username, user_data["password"])