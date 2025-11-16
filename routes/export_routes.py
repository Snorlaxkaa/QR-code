"""
Excel 匯出相關功能
"""
from flask import request, send_file
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment
from datetime import datetime
import os
from db import get_connection


def register_export_routes(app):
    """註冊匯出相關的路由"""
    
    # ----------- 匯出資料（改為匯出搜尋結果）-----------
    @app.route('/export_xlsx', methods=['GET', 'POST'])
    def export_xlsx():
        nid = request.values.get('nid')
        date_start = request.values.get('date_start')
        date_end = request.values.get('date_end')

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # ✅ 基本查詢
        query = """
            SELECT name, id_number, service_start, service_end,
                   service_item, service_content, service_hours, service_minutes,
                   served_people_count, transport_fee, meal_fee, service_area,
                   remarks, import_action, foreign_service_count, domestic_service_count
            FROM service_records
            WHERE 1=1
        """
        params = []

        # ✅ 條件（依據輸入）
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

        cursor.execute(query, tuple(params))
        records = cursor.fetchall()
        cursor.close()
        conn.close()

        # ✅ 生成 Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Search Results"

        if records:
            header_map = {
                "name": "姓名",
                "id_number": "身分證",
                "service_start": "上班時間",
                "service_end": "下班時間",
                "service_item": "服務項目",
                "service_content": "服務內容",
                "service_hours": "工時",
                "service_minutes": "分鐘",
                "served_people_count": "服務人數",
                "transport_fee": "交通費",
                "meal_fee": "餐費",
                "service_area": "服務地區",
                "remarks": "備註",
                "import_action": "匯入動作",
                "foreign_service_count": "海外服務",
                "domestic_service_count": "國內服務"
            }

            keys = [k for k in records[0].keys() if k in header_map]
            ws.append([header_map[k] for k in keys])

            # 設定標題列置中對齊
            for cell in ws[1]:
                cell.alignment = Alignment(horizontal='center', vertical='center')

            for r in records:
                for k, v in r.items():
                    if v is None:
                        r[k] = ""
                row = ws.append([r[k] for k in keys])
                # 設定資料列置中對齊
                for cell in ws[ws.max_row]:
                    cell.alignment = Alignment(horizontal='center', vertical='center')

            # ✅ 自動欄寬（優化版）
            def get_column_width(cell_value):
                if cell_value is None:
                    return 0
                if isinstance(cell_value, datetime):
                    return 20  # 日期時間固定寬度
                
                str_value = str(cell_value)
                # 計算中文字元的數量
                chinese_count = sum(1 for char in str_value if '\u4e00' <= char <= '\u9fff')
                # 其他字元的數量
                other_count = len(str_value) - chinese_count
                # 中文字元寬度為 2.1，其他字元為 1
                return chinese_count * 2.1 + other_count

            for col in ws.columns:
                max_length = max(get_column_width(cell.value) for cell in col)
                ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

        # ✅ 儲存與回傳
        # 設定檔名
        if date_start or date_end:
            # 有日期範圍的情況
            if date_start and date_end:
                filename = f"工時紀錄_{date_start}至{date_end}"
            elif date_start:
                filename = f"工時紀錄_{date_start}起"
            elif date_end:
                filename = f"工時紀錄_至{date_end}"
                
            # 如果有身分證號，加到檔名前面
            if nid:
                filename = f"{nid}_{filename}"
            
            filename += ".xlsx"
        else:
            # 只有身分證號或完全沒有搜尋條件
            if nid:
                filename = f"{nid}.xlsx"
            else:
                filename = f"全部資料_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        file_path = os.path.join(os.getcwd(), filename)
        wb.save(file_path)
        return send_file(file_path, as_attachment=True)
