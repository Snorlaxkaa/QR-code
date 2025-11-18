import cv2
from datetime import datetime, timedelta
import os
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
from db import insert_check_in, update_check_out

# ---------- 顏色設定 ----------
if os.name == 'nt':
    os.system('color')

class Colors:
    RESET = '\033[0m'; BOLD = '\033[1m'
    RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
    BLUE = '\033[94m'; PURPLE = '\033[95m'; CYAN = '\033[96m'

# ---------- 加密/解密設定 ----------
SECRET_PASSPHRASE = "MyVeryStrongSecretPassword"  # 請確認與 app.py 相同

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

def decrypt_payload(payload: str):
    """解密 QRCode payload"""
    try:
        data = json.loads(payload)
        ct = data["ct"]
        return FERNET.decrypt(ct.encode()).decode()
    except Exception:
        # 如果解密失敗，可能是未加密的 QRCode，直接返回原始內容
        return payload

# ---------- 工具 ----------
def split_after_colon(s: str):
    for c in (":", "："):
        if c in s:
            return s.split(c, 1)[1].strip()
    return ""

def parse_qr_text(data: str):
    lines = [ln.strip() for ln in data.replace("\r\n", "\n").split("\n") if ln.strip()]
    name = nid = ""
    for ln in lines:
        low = ln.lower()
        if ("姓名" in ln or low.startswith("name")) and (":" in ln or "：" in ln):
            name = split_after_colon(ln)
        elif ("身分證" in ln or "身份證" in ln or low.startswith(("id ", "id:", "idno", "id no", "id number"))) and (":" in ln or "：" in ln):
            nid = split_after_colon(ln)
    if not (name or nid):
        if len(lines) > 0: name = lines[0]
        if len(lines) > 1: nid  = lines[1]
    if not name: name = "未提供"
    if not nid:  nid  = "未提供"
    return {"name": name, "nid": nid}

# ---------- 相機 ----------
def open_camera_try(indices=(1, 0)):
    for idx in indices:
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if cap.isOpened():
            return cap, idx
        cap.release()
    return None, None

# ---------- 主程式 ----------
def main():
    cap, cam_idx = open_camera_try((1, 0))
    if cap is None:
        print(f"{Colors.RED}❌ [ERROR] 無法開啟攝影機{Colors.RESET}")
        return

    detector = cv2.QRCodeDetector()
    last_seen = {}
    clock_records = {}

    print(f"{Colors.GREEN}🎯 QR Code 打卡系統啟動（支援加密 QRCode）{Colors.RESET}")
    print(f"{Colors.CYAN}📱 第一次掃 → 上班打卡 | 第二次掃 → 下班打卡{Colors.RESET}")

    while True:
        ok, frame = cap.read()
        if not ok:
            continue

        retval, decoded_info, points, _ = detector.detectAndDecodeMulti(frame)
        if retval and points is not None:
            for data, pts in zip(decoded_info, points):
                data = (data or "").strip()
                if not data:
                    continue

                now = datetime.now()
                if data in last_seen and now - last_seen[data] < timedelta(seconds=3):
                    continue
                last_seen[data] = now

                # 🔓 嘗試解密 QRCode
                try:
                    decrypted_data = decrypt_payload(data)
                    print(f"{Colors.BLUE}🔓 解密成功{Colors.RESET}")
                    print(f"{Colors.CYAN}解密內容：\n{decrypted_data}{Colors.RESET}")
                except Exception as e:
                    # 解密失敗，使用原始資料
                    decrypted_data = data
                    print(f"{Colors.YELLOW}ℹ️  使用未加密的 QRCode{Colors.RESET}")

                info = parse_qr_text(decrypted_data)
                nid, name = info["nid"], info["name"]

                # 打卡邏輯
                if nid not in clock_records or "end" in clock_records[nid]:
                    # 上班打卡
                    clock_records[nid] = {"name": name, "start": now}
                    insert_check_in(name, nid, now)
                    print(f"{Colors.GREEN}🌅 {name} 上班打卡成功 - {now.strftime('%Y/%m/%d %H:%M:%S')}{Colors.RESET}")
                else:
                    # 下班打卡
                    start_time = clock_records[nid]["start"]
                    end_time = now
                    delta = end_time - start_time
                    hours, remainder = divmod(delta.total_seconds(), 3600)
                    minutes = int(remainder // 60)
                    update_check_out(nid, end_time, int(hours), minutes)
                    clock_records[nid]["end"] = end_time
                    print(f"{Colors.YELLOW}🌙 {name} 下班打卡成功 - {end_time.strftime('%Y/%m/%d %H:%M:%S')}，工時 {int(hours)}小時 {minutes}分{Colors.RESET}")

        cv2.imshow("QR 打卡系統", frame)
        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"{Colors.PURPLE}🔚 程式結束{Colors.RESET}")

if __name__ == "__main__":
    main()