# QR Code 服務記錄系統 - 專案結構

## 📁 檔案架構

```
QR code/
│
├── app.py                      # 主應用程式入口
├── config.py                   # Flask 應用配置
├── db.py                       # 資料庫連線和基本操作
├── user.py                     # 使用者認證模組
├── qr_scanner.py              # QR code 掃描功能
├── qr-test.py                 # 測試檔案
├── test.py                    # 測試檔案
│
├── routes/                     # 路由模組（按功能分類）
│   ├── __init__.py            # 套件初始化
│   ├── auth_routes.py         # 登入/登出路由
│   ├── record_routes.py       # 服務記錄查詢、編輯、刪除
│   ├── export_routes.py       # Excel 匯出功能
│   └── qrcode_routes.py       # QRCode 生成路由
│
├── templates/                  # HTML 模板
│   ├── index.html
│   ├── login.html
│   ├── edit.html
│   └── QRcode.html
│
└── __pycache__/               # Python 快取檔案
```

## 🚀 模組說明

### 核心模組

- **app.py** - 應用程式的主進入點，負責應用配置和路由註冊
- **config.py** - Flask 應用配置，包含 Flask-Login 初始化
- **db.py** - 資料庫連線管理和基本操作
- **user.py** - 使用者認證系統

### 路由模組 (routes/)

#### 1. **auth_routes.py** - 認證模組
   - `/login` - 登入頁面 (GET, POST)
   - `/logout` - 登出功能 (GET)

#### 2. **record_routes.py** - 服務記錄管理
   - `/` 及 `/index` - 後台主頁，顯示所有服務記錄 (GET, POST)
   - `/edit/<serial_no>` - 編輯服務記錄 (GET, POST)
   - `/delete/<serial_no>` - 刪除服務記錄 (GET)
   
#### 3. **export_routes.py** - 資料匯出
   - `/export_xlsx` - 匯出搜尋結果到 Excel (GET, POST)
   
#### 4. **qrcode_routes.py** - QRCode 管理
   - `/qrcode` - 生成 QRCode (GET, POST)

## 📦 依賴套件

```
Flask
Flask-Login
mysql-connector-python
openpyxl
qrcode
Pillow
```

## 🔑 主要特性

✅ **模組化設計** - 程式碼按功能清晰分類
✅ **登入驗證** - 使用 Flask-Login 的認證系統
✅ **資料庫操作** - 完整的 CRUD 功能
✅ **Excel 匯出** - 支援搜尋結果批量匯出
✅ **QRCode 生成** - 動態生成人員 QRCode
✅ **分頁功能** - 大量資料的頁面顯示優化

## 🚀 如何執行

```bash
python app.py
```

預設運行於 `http://localhost:5000`

## 📝 登入憑證

預設管理員帳號：
- 帳號：`admin`
- 密碼：`0000`

---

**開發日期**: 2025年11月14日
**版本**: 1.0 (模組化重構版)
