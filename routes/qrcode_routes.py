"""
QRCode 生成相關路由
"""
from flask import render_template, request, flash
import qrcode
from qrcode.constants import ERROR_CORRECT_Q
import base64
import io


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
                qr_text = f"姓名：{name}\n身分證字號：{id_number}"
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=ERROR_CORRECT_Q,
                    box_size=10,
                    border=4
                )
                qr.add_data(qr_text)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                qr_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        return render_template("QRcode.html", qr_base64=qr_base64, user_name=user_name)
