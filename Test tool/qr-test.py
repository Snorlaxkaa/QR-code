# -- coding: utf-8 --
import cv2
import json
import time
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64

# 固定密語（請確認與 app.py 完全相同）
SECRET_PASSPHRASE = "MyVeryStrongSecretPassword"

# ------------------------------------------------
# 由固定密語產生固定金鑰（與 app.py 相同邏輯）
# ------------------------------------------------
def make_key(passphrase):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"fixed_salt_16b",  # 固定 salt
        iterations=390000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

FERNET = Fernet(make_key(SECRET_PASSPHRASE))

# ------------------------------------------------
# 解密 QRCode payload
# ------------------------------------------------
def decrypt_payload(payload: str):
    data = json.loads(payload)
    ct = data["ct"]
    return FERNET.decrypt(ct.encode()).decode()

def main():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    print("📷 請將加密 QRCode 對準鏡頭 ...")
    print("（成功解密後會暫停 3 秒，再繼續等待下一位）")

    # 用來避免在同一段時間內重複觸發
    in_cooldown = False
    cooldown_start = 0.0
    COOLDOWN_SECONDS = 3

    while True:
        ok, frame = cap.read()
        if not ok:
            continue

        # 若在冷卻中，只顯示畫面但不處理解碼結果
        if in_cooldown:
            # 檢查冷卻是否結束
            if time.time() - cooldown_start >= COOLDOWN_SECONDS:
                in_cooldown = False
                print("✅ 冷卻結束，可以掃描下一位。")
            cv2.imshow("QRCode Scanner", frame)
            if (cv2.waitKey(1) & 0xFF) == ord("q"):
                break
            continue

        data, bbox, _ = detector.detectAndDecode(frame)

        if data:
            try:
                plaintext = decrypt_payload(data)

                print("\n===== 🟢 解密成功 =====")
                print(plaintext)
                print("==========================\n")

                # 進入 3 秒冷卻，不再重複觸發
                in_cooldown = True
                cooldown_start = time.time()
                print("⏳ 3 秒冷卻中，請讓下一位準備 QRCode ...")

            except Exception as e:
                print(f"❌ 解密失敗：{e}")

        cv2.imshow("QRCode Scanner", frame)

        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("🔚 程式已結束")

if __name__ == "__main__":
    main()