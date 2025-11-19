"""
QR Code 服務記錄系統 - 主應用程式
"""
from config import create_app
from routes.auth_routes import register_auth_routes
from routes.record_routes import register_record_routes
from routes.export_routes import register_export_routes
from routes.qrcode_routes import register_qrcode_routes
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from functools import wraps
app = Flask(__name__)
app.secret_key = "super_secret_key_123" # 記得之後要改複雜一點

# --- 🔐 登入檢查裝飾器 (新增這段) ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 檢查 session 中是否有 'user'
        if 'user' not in session:
            flash('⛔ 請先登入系統', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
# 建立 Flask 應用程式
app = create_app()

# 註冊各個功能模組的路由
register_auth_routes(app)
register_record_routes(app)
register_export_routes(app)
register_qrcode_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
