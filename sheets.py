print("✅ credentials loaded:", config.GOOGLE_CREDENTIALS_JSON is not None)
# sheets.py

import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import config

# ✅ 用環境變數讀取 credentials JSON，建立連線
service_account_info = json.loads(config.GOOGLE_CREDENTIALS_JSON)
credentials = Credentials.from_service_account_info(service_account_info)
gc = gspread.authorize(credentials)

# ✅ 開啟活動清單主表（整年度活動清單）
sh = gc.open_by_key(config.EVENTS_SPREADSHEET_ID)
event_list_ws = sh.worksheet("活動清單")  # 預設名稱，請依實際調整

# 讀取所有活動表名稱
def get_event_sheet_names():
    return [sheet.title for sheet in sh.worksheets() if sheet.title != "活動清單"]

# 讀取活動清單資料（用來顯示目前有哪些活動可報名）
def get_event_list():
    data = event_list_ws.get_all_records()
    return data  # 每筆是 dict：{"日期": ..., "時段": ..., "活動名稱": ...}

# 報名某活動（根據活動表格名稱）
def add_signup(sheet_name, name, line_name, phone, number, note):
    try:
        ws = sh.worksheet(sheet_name)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ws.append_row([now, name, line_name, phone, number, note])
        return True
    except Exception as e:
        print("報名錯誤：", e)
        return False

# 取消報名（根據 LINE 名稱 + 活動名稱搜尋）
def cancel_signup(sheet_name, line_name):
    try:
        ws = sh.worksheet(sheet_name)
        records = ws.get_all_records()
        for i, row in enumerate(records):
            if row.get("LINE名稱") == line_name:
                ws.delete_rows(i + 2)  # 加2：因為有標題列 + index從0起
                return True
        return False
    except Exception as e:
        print("取消報名錯誤：", e)
        return False

# 查詢使用者參加了哪些活動（根據 LINE 名稱）
def get_user_signups(line_name):
    joined = []
    for ws in sh.worksheets():
        if ws.title == "活動清單":
            continue
        records = ws.get_all_records()
        for row in records:
            if row.get("LINE名稱") == line_name:
                joined.append(ws.title)
    return joined

# 管理者查詢所有報名資料（依照所有活動彙整）
def get_admin_all_data():
    all_data = {}
    for ws in sh.worksheets():
        if ws.title == "活動清單":
            continue
        records = ws.get_all_records()
        all_data[ws.title] = records
    return all_data
