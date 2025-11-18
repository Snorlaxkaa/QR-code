"""
修復管理員權限腳本
確保 admin 帳號具有管理員權限
"""
from db import get_connection
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def check_and_fix_admin():
    """檢查並修復 admin 帳號"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("=" * 60)
    print("🔧 管理員權限修復工具")
    print("=" * 60)
    print()
    
    # 檢查 admin 是否存在
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin = cursor.fetchone()
    
    if not admin:
        print("❌ admin 帳號不存在，正在建立...")
        
        # 建立 admin 帳號
        password_hash = bcrypt.generate_password_hash('0000').decode('utf-8')
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                ('admin', password_hash, 'admin')
            )
            conn.commit()
            print("✅ 已建立 admin 帳號")
            print("   帳號: admin")
            print("   密碼: 0000")
            print("   權限: admin (管理員)")
        except Exception as e:
            print(f"❌ 建立失敗: {e}")
            cursor.close()
            conn.close()
            return False
    else:
        print("✅ admin 帳號存在")
        print(f"   ID: {admin['id']}")
        print(f"   帳號: {admin['username']}")
        print(f"   當前權限: {admin.get('role', '未設定')}")
        
        # 檢查權限
        if admin.get('role') != 'admin':
            print("\n⚠️  發現問題：admin 不是管理員權限！")
            print("正在修復...")
            
            try:
                cursor.execute(
                    "UPDATE users SET role = 'admin' WHERE username = 'admin'"
                )
                conn.commit()
                print("✅ 已將 admin 設定為管理員權限")
            except Exception as e:
                print(f"❌ 修復失敗: {e}")
                cursor.close()
                conn.close()
                return False
        else:
            print("✅ 權限正確（管理員）")
    
    print()
    
    # 顯示所有使用者
    print("📋 目前所有使用者：")
    cursor.execute("SELECT id, username, role, created_at FROM users")
    users = cursor.fetchall()
    
    if users:
        print(f"\n{'ID':<5} {'帳號':<15} {'權限':<10} {'建立時間'}")
        print("-" * 60)
        for user in users:
            print(f"{user['id']:<5} {user['username']:<15} {user['role']:<10} {user['created_at']}")
    else:
        print("沒有任何使用者")
    
    cursor.close()
    conn.close()
    
    print()
    print("=" * 60)
    print("✨ 修復完成！")
    print("=" * 60)
    print()
    print("現在可以使用以下帳號登入：")
    print("帳號: admin")
    print("密碼: 0000")
    print()
    print("然後就可以註冊新使用者了！")
    
    return True


if __name__ == "__main__":
    check_and_fix_admin()