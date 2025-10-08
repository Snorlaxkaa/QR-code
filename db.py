import mysql.connector

# ---------- 資料庫設定 ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "0000",
    "database": "personnel_data"
}

# ---------- 建立連線 ----------
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ---------- 上班打卡 ----------
def insert_check_in(name, nid, check_in):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO service_records (name, id_number, service_start)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (name, nid, check_in))
    conn.commit()
    cursor.close()
    conn.close()

# ---------- 下班打卡 ----------
def update_check_out(nid, check_out, hours, minutes):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        UPDATE service_records 
        SET service_end = %s, service_hours = %s, service_minutes = %s
        WHERE id_number = %s AND service_end IS NULL
        ORDER BY serial_no DESC LIMIT 1
    """
    cursor.execute(sql, (check_out, hours, minutes, nid))
    conn.commit()
    cursor.close()
    conn.close()
