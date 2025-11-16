"""
登入/登出相關路由
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from user import User


def register_auth_routes(app):
    """註冊認證相關的路由"""
    
    # ----------- 登入頁面 -----------
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.get_by_username(username)
            
            if user and user.password == password:
                login_user(user)
                flash('登入成功！', 'success')
                return redirect(url_for('admin_panel'))
            else:
                flash('帳號或密碼錯誤！', 'error')
        
        return render_template('login.html')

    # ----------- 登出 -----------
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('已登出！', 'success')
        return redirect(url_for('login'))
