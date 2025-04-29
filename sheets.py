import config
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

# 初始化 Google Sheets API
def init_gspread_client():
    assert config.GOOGLE_CREDENTIALS_JSON is not None, "❌ GOOGLE_CREDENTIALS_JSON 環境變數為 None"
    credentials_info = json.loads(config.GOOGLE_CREDENTIALS_JSON)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(credentials)
    return client

# 取得活動清單
def get_event_list():
    client = init_gspread_client()
    sheet = client.open_by_key(config.EVENTS_SPREADSHEET_ID).sheet1
    events = []
    for record in sheet.get_all_records():
        if record.get("活動名稱") and record.get("日期") and record.get("時段"):
            events.append({
                "活動名稱": record["活動名稱"],
                "日期": record["日期"],
                "時段": record["時段"]
            })
    return events

# 報名資料寫入
def add_signup(sheet_name, name, user_id, phone, number, note):
    try:
        client = init_gspread_client()
        sheet = client.open(sheet_name).sheet1
        sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, user_id, phone, number, note])
        return True
    except Exception as e:
        print(f"[add_signup] error: {e}")
        return False

# 查詢使用者已報名活動
def get_user_signups(user_id):
    client = init_gspread_client()
    spreadsheet = client.open_by_key(config.EVENTS_SPREADSHEET_ID)
    joined = []
    for ws in spreadsheet.worksheets():
        for record in ws.get_all_records():
            if str(record.get("user_id")) == str(user_id):
                joined.append(f"{ws.title} - {record.get('name')}")
    return joined

# 管理員查詢所有資料
def get_admin_all_data():
    client = init_gspread_client()
    spreadsheet = client.open_by_key(config.EVENTS_SPREADSHEET_ID)
    all_data = {}
    for ws in spreadsheet.worksheets():
        all_data[ws.title] = ws.get_all_records()
    return all_data

# 取消報名
def cancel_signup(sheet_name, line_name):
    try:
        client = init_gspread_client()
        sheet = client.open(sheet_name).sheet1
        records = sheet.get_all_records()
        for idx, record in enumerate(records):
            if record.get("LINE名稱") == line_name:
                sheet.delete_rows(idx + 2)
                return True
        return False
    except Exception as e:
        print(f"[cancel_signup] error: {e}")
        return False
