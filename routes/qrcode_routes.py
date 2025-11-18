"""
QRCode 生成相關路由
"""
from flask import render_template, request, flash
import qrcode
from qrcode.constants import ERROR_CORRECT_Q
import base64
import io
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

# ---------- 加密設定 ----------
SECRET_PASSPHRASE = "MyVeryStrongSecretPassword"  # 請與 qr_scanner.py 保持一致

def make_key(passphrase):
    """由固定密語產生固定金鑰"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"fixed_salt_16b",  # 固定 salt
        iterations=390000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

FERNET = Fernet(make_key(SECRET_PASSPHRASE))

def encrypt_payload(plaintext: str) -> str:
    """加密 QRCode payload"""
    ct = FERNET.encrypt(plaintext.encode()).decode()
    return json.dumps({"ct": ct})


def register_qrcode_routes(app):
    """註冊 QRCode 相關的路由"""
    
    # ----------- 生成 QRcode -----------
    @app.route("/qrcode", methods=["GET", "POST"])
    def qrcode_page():
        qr_base64 = None
        user_name = None

        if request.method == "POST":
            name = request.form.get("name")
            id_number = request.form.get("id_number")

            if not name or not id_number:
                flash("請完整輸入姓名與身分證字號！")
            else:
                user_name = name
                # 原始明文
                qr_text = f"姓名：{name}\n身分證字號：{id_number}"
                
                # 🔐 加密處理
                encrypted_text = encrypt_payload(qr_text)
                
                # 生成 QRCode
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=ERROR_CORRECT_Q,
                    box_size=10,
                    border=4
                )
                qr.add_data(encrypted_text)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                qr_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        return render_template("QRcode.html", qr_base64=qr_base64, user_name=user_name)