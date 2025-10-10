from flask import Flask, render_template, request
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# ---------- 資料庫設定 ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "0000",
    "database": "personnel_data"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ---------- 查詢員工當月資料 ----------
def get_monthly_records(nid):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT name, id_number, service_start, service_end, service_hours, service_minutes
        FROM service_records
        WHERE id_number = %s
        AND MONTH(service_start) = MONTH(CURDATE())
        AND YEAR(service_start) = YEAR(CURDATE())
        ORDER BY service_start
    """
    cursor.execute(sql, (nid,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # 計算總工時
    total_hours = 0
    total_minutes = 0
    for r in rows:
        total_hours += r["service_hours"] or 0
        total_minutes += r["service_minutes"] or 0

    # 轉換分鐘為小時
    total_hours += total_minutes // 60
    total_minutes = total_minutes % 60

    return rows, total_hours, total_minutes

@app.route("/", methods=["GET", "POST"])
def index():
    records = []
    total_hours = 0
    total_minutes = 0
    nid = ""

    if request.method == "POST":
        nid = request.form.get("nid")
        if nid:
            records, total_hours, total_minutes = get_monthly_records(nid)

    return render_template(
        "index.html",
        records=records,
        nid=nid,
        total_hours=total_hours,
        total_minutes=total_minutes
    )

if __name__ == "__main__":
    app.run(debug=True)
