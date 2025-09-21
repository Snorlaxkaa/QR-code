import cv2
from datetime import datetime
import sys
import os

# 設定 Windows 終端支援 ANSI 色彩碼
if os.name == 'nt':
    os.system('color')

# ANSI 色彩碼定義
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # 背景色
    BG_BLACK = '\033[40m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'

# ---------- 視覺標註：在 QR 外框上方顯示一小段文字 ----------
def draw_bbox(frame, pts, text):
    pts = pts.reshape(-1, 2).astype(int)
    for i in range(4):
        p1 = tuple(pts[i])
        p2 = tuple(pts[(i + 1) % 4])
        cv2.line(frame, p1, p2, (0, 255, 0), 2)
    display = text.replace("\r", " ").replace("\n", " / ")
    display = display if len(display) <= 60 else display[:57] + "..."
    x, y = pts[0]
    y = max(30, y)
    cv2.rectangle(frame, (x, y - 25), (x + 10 + 8 * len(display), y), (0, 255, 0), -1)
    cv2.putText(frame, display, (x + 5, y - 7),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

# ---------- 工具：分隔中/英冒號 ----------
def split_after_colon(s: str):
    for c in (":", "："):
        if c in s:
            return s.split(c, 1)[1].strip()
    return ""

# ---------- 解析三行（姓名 / 員工編號 / 身分證字號），不足則填「未提供」 ----------
def parse_qr_text(data: str):
    """
    期待格式（兩者皆可）：
      1) 三行無標籤：
         第1行：姓名
         第2行：員工編號
         第3行：身分證字號
      2) 含標籤（任一同義都可）：
         姓名: 王小明
         員工編號: A001
         身分證字號: A123456789   （也接受：身分證 / 身份證 / 身份證字號 / ID / ID No / ID Number）
    """
    lines = [ln.strip() for ln in data.replace("\r\n", "\n").split("\n") if ln.strip()]

    name = emp = nid = ""

    # 先試著吃帶標籤的情況
    for ln in lines:
        low = ln.lower()
        if ("姓名" in ln or low.startswith("name")) and (":" in ln or "：" in ln):
            name = split_after_colon(ln)
        elif ("員工編號" in ln or low.startswith(("employee", "emp"))) and (":" in ln or "：" in ln):
            emp = split_after_colon(ln)
        elif (
            "身分證" in ln or "身份證" in ln or
            low.startswith(("id ", "id:", "idno", "id no", "id number"))
        ) and (":" in ln or "：" in ln):
            nid = split_after_colon(ln)

    # 若沒有任何標籤，就按行序帶入
    if not (name or emp or nid):
        if len(lines) > 0: name = lines[0]
        if len(lines) > 1: emp  = lines[1]
        if len(lines) > 2: nid  = lines[2]

    # 保底填值
    if not name: name = "未提供"
    if not emp:  emp  = "未提供"
    if not nid:  nid  = "未提供"
    return {"name": name, "emp": emp, "nid": nid}

# ---------- 左側資訊面板 ----------
def draw_side_panel(frame, info):
    if not info:
        return
    h, w = frame.shape[:2]
    panel_w = min(420, int(w * 0.45))

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (panel_w, 130), (0, 0, 0), -1)   # 半透明底
    cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)

    x0, y0, lh = 12, 32, 32
    cv2.putText(frame, f"姓名：{info['name']}", (x0, y0),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"員工編號：{info['emp']}", (x0, y0 + lh),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"身分證字號：{info['nid']}", (x0, y0 + 2 * lh),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2, cv2.LINE_AA)

# ---------- 相容不同 OpenCV 版本 ----------
def decode_multi(detector, frame):
    result = detector.detectAndDecodeMulti(frame)
    data_list, points = [], None
    if isinstance(result, tuple):
        if len(result) == 4:
            # 新版：retval, decoded_info, points, straight_qrcode
            retval, decoded_info, points, _ = result
            data_list = decoded_info if retval else []
        elif len(result) == 3:
            # 舊版：decoded_info, points, straight_qrcode
            decoded_info, points, _ = result
            data_list = decoded_info
    return data_list, points

def open_camera_try(indices=(1, 0)):
    """依序嘗試多個 index 開啟攝影機（Windows 優先用 CAP_DSHOW）"""
    for idx in indices:
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if cap.isOpened():
            return cap, idx
        cap.release()
    return None, None

def main():
    cap, cam_idx = open_camera_try((1, 0))
    if cap is None:
        print(f"{Colors.RED}❌ [ERROR] 無法開啟攝影機（嘗試索引 1 與 0 皆失敗）。{Colors.RESET}")
        return

    # (可選) 降低解析度以提升偵測速度與延遲
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    detector = cv2.QRCodeDetector()
    last_info = {"name": "未提供", "emp": "未提供", "nid": "未提供"}
    seen = set()

    # 美化的啟動訊息
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}🎯 QR Code 身分識別系統已啟動{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}📷 攝影機索引: {Colors.YELLOW}{cam_idx}{Colors.RESET}")
    print(f"{Colors.BLUE}📱 請將 QR Code 對準攝影機{Colors.RESET}")
    print(f"{Colors.PURPLE}⚡ 按 'q' 鍵離開程式{Colors.RESET}")
    print(f"{Colors.CYAN}{'-' * 60}{Colors.RESET}")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print(f"{Colors.YELLOW}⚠️  [WARN] 讀取畫面失敗，重試中...{Colors.RESET}")
                continue

            data_list, points = decode_multi(detector, frame)

            if points is not None and len(points) > 0:
                for data, pts in zip(data_list, points):
                    data = (data or "").strip()
                    if not data:
                        continue

                    # 外框提示
                    draw_bbox(frame, pts, data)

                    # 解析資訊（同一段文字只處理一次）
                    if data not in seen:
                        seen.add(data)
                        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        info = parse_qr_text(data)
                        last_info = info
                        
                        # 美化的掃描結果輸出
                        print(f"\n{Colors.GREEN}🔍 {'=' * 50}{Colors.RESET}")
                        print(f"{Colors.CYAN}⏰ 掃描時間: {Colors.WHITE}{ts}{Colors.RESET}")
                        print(f"{Colors.BOLD}📋 識別結果:{Colors.RESET}")
                        print(f"   {Colors.BLUE}👤 姓名: {Colors.GREEN}{Colors.BOLD}{info['name']}{Colors.RESET}")
                        print(f"   {Colors.BLUE}🏢 員工編號: {Colors.YELLOW}{Colors.BOLD}{info['emp']}{Colors.RESET}")
                        print(f"   {Colors.BLUE}🆔 身分證字號: {Colors.PURPLE}{Colors.BOLD}{info['nid']}{Colors.RESET}")
                        print(f"{Colors.GREEN}{'=' * 52}{Colors.RESET}")

            # 畫左側資訊面板（顯示最近一次成功解析出的三欄）
            draw_side_panel(frame, last_info)

            cv2.putText(frame, "Press 'q' to quit",
                        (10, frame.shape[0] - 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow("QR Text → 姓名/員工編號/身分證字號", frame)

            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"\n{Colors.PURPLE}🔚 {'=' * 50}{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ 程式已安全結束，感謝使用！{Colors.RESET}")
        print(f"{Colors.PURPLE}{'=' * 52}{Colors.RESET}")

if __name__ == "__main__":
    main()
