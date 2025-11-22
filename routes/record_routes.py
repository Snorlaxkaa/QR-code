"""
服務記錄查詢和管理相關路由
"""
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from db import get_connection


def register_record_routes(app):
    """註冊服務記錄相關的路由"""
    
    # ----------- 後台主頁 -----------
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/index', methods=['GET', 'POST'])
    @login_required
    def admin_panel():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # --- 基本參數 ---
        all_records_page = request.args.get('all_records_page', 1, type=int)
        per_page = 30

        # --- 獲取所有記錄 ---
        cursor.execute("SELECT * FROM service_records ORDER BY serial_no DESC")
        all_records_data = cursor.fetchall()
        
        # --- 計算分頁 ---
        total_all_records = len(all_records_data)
        total_all_pages = max(1, (total_all_records + per_page - 1) // per_page)
        all_records_page = max(1, min(all_records_page, total_all_pages))
        
        # --- 對記錄進行分頁 ---
        start_idx_all = (all_records_page - 1) * per_page
        end_idx_all = start_idx_all + per_page
        records = all_records_data[start_idx_all:end_idx_all]
        
        cursor.close()
        conn.close()

        return render_template(
            'index.html',
            records=records,
            user=current_user.username,
            all_records_page=all_records_page,
            total_all_pages=total_all_pages,
            total_all_records=total_all_records
        )

    # ----------- 搜尋頁面 -----------
    @app.route('/search', methods=['GET', 'POST'])
    @login_required
    def search_page():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # --- 基本參數 ---
        nid = request.args.get('nid', '').strip()
        date_start = request.args.get('date_start')
        date_end = request.args.get('date_end')
        page = request.args.get('page', 1, type=int)
        per_page = 30

        print(f"搜尋參數：nid={nid}, date_start={date_start}, date_end={date_end}")

        # --- 驗證日期格式 ---
        for var_name, var_value in [('開始日期', date_start), ('結束日期', date_end)]:
            if var_value:
                try:
                    datetime.strptime(var_value, '%Y-%m-%d')
                except ValueError:
                    flash(f'{var_name}格式不正確', 'error')
                    if var_name == '開始日期': date_start = None
                    else: date_end = None

        # --- 組合查詢 ---
        query = """
            SELECT serial_no, name, id_number, service_start, service_end,
                   service_item, service_content, service_hours, service_minutes,
                   served_people_count, transport_fee, meal_fee, service_area,
                   remarks, import_action, serial_number, foreign_service_count, domestic_service_count
            FROM service_records
            WHERE 1=1
        """
        params = []

        if nid:
            query += " AND LOWER(id_number) = LOWER(%s)"
            params.append(nid)

        if date_start and date_end:
            query += " AND DATE(service_start) BETWEEN %s AND %s"
            params.extend([date_start, date_end])
        elif date_start:
            query += " AND DATE(service_start) >= %s"
            params.append(date_start)
        elif date_end:
            query += " AND DATE(service_start) <= %s"
            params.append(date_end)

        query += " ORDER BY service_start DESC"

        # --- 執行查詢 ---
        cursor.execute(query, tuple(params))
        all_records = cursor.fetchall()

        # --- 分頁 ---
        total_records = len(all_records)
        total_pages = max(1, (total_records + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        current_page_records = all_records[start_idx:end_idx]

        # --- 計算總工時 ---
        total_hours = sum(r.get('service_hours') or 0 for r in all_records)
        total_minutes = sum(r.get('service_minutes') or 0 for r in all_records)
        total_hours += total_minutes // 60
        total_minutes = total_minutes % 60

        cursor.close()
        conn.close()

        return render_template(
            'search.html',
            personal_records=current_page_records,
            nid=nid,
            total_hours=total_hours,
            total_minutes=total_minutes,
            date_start=date_start,
            date_end=date_end,
            page=page,
            total_pages=total_pages,
            total_records=total_records
        )

    # ----------- 編輯資料 -----------
    @app.route('/edit/<int:serial_no>', methods=['GET', 'POST'])
    def edit(serial_no):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            fields = [
                'name', 'id_number', 'service_start', 'service_end',
                'service_item', 'service_content', 'service_hours', 'service_minutes',
                'served_people_count', 'transport_fee', 'meal_fee',
                'service_area', 'remarks', 'import_action', 'serial_number',
                'foreign_service_count', 'domestic_service_count'
            ]

            values = []
            for f in fields:
                v = request.form.get(f)
                
                # 處理日期時間格式
                if f in ['service_start', 'service_end'] and v:
                    try:
                        v = datetime.strptime(v, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:00')
                    except ValueError:
                        v = None
                
                # 處理數值欄位
                elif f in ["service_hours", "service_minutes", "served_people_count",
                          "transport_fee", "meal_fee",
                          "foreign_service_count", "domestic_service_count"]:
                    try:
                        v = int(v) if v and v.strip() else 0
                    except ValueError:
                        v = 0
                
                # 處理其他可為空的欄位
                elif v is None or v.strip() == "":
                    v = None
                    
                values.append(v)

            values.append(serial_no)

            sql = """
                UPDATE service_records
                SET name=%s, id_number=%s, service_start=%s, service_end=%s,
                    service_item=%s, service_content=%s, service_hours=%s, service_minutes=%s,
                    served_people_count=%s, transport_fee=%s, meal_fee=%s,
                    service_area=%s, remarks=%s, import_action=%s, serial_number=%s,
                    foreign_service_count=%s, domestic_service_count=%s
                WHERE serial_no=%s
            """
            try:
                cursor.execute(sql, tuple(values))
                conn.commit()
                flash("✅ 資料已更新", "success")
            except Exception as e:
                flash(f"❌ 錯誤：{e}", "error")
            finally:
                cursor.close()
                conn.close()
            return redirect(url_for('admin_panel'))

        # 讀取指定編號資料
        cursor.execute("SELECT * FROM service_records WHERE serial_no = %s", (serial_no,))
        record = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit.html', record=record)

    # ----------- 刪除資料 -----------
    @app.route('/delete/<int:serial_no>')
    def delete(serial_no):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM service_records WHERE serial_no = %s", (serial_no,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('資料已刪除', 'info')
        return redirect(url_for('admin_panel'))