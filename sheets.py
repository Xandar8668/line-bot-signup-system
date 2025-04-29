import config
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

# 初始化 Google Sheets API
def init_gspread_client():
    credentials_info = json.loads(config.GOOGLE_CREDENTIALS_JSON)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(credentials)
    return client

# 取得活動清單
def get_event_list():
    client = init_gspread_client()
    sheet = client.open_by_key(config.EVENTS_SPREADSHEET_ID).sheet1  # 活動清單在第一個 sheet

    events = []
    records = sheet.get_all_records()

    for record in records:
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
    sheet_names = [ws.title for ws in spreadsheet.worksheets()]

    joined_events = []

    for sheet_name in sheet_names:
        try:
            ws = spreadsheet.worksheet(sheet_name)
            records = ws.get_all_records()
            for record in records:
                if str(record.get("user_id")) == str(user_id):
                    joined_events.append(f"{sheet_name} - {record.get('name')}")
        except Exception as e:
            print(f"[get_user_signups] error on {sheet_name}: {e}")

    return joined_events

# 管理者查詢所有場次資料
def get_admin_all_data():
    client = init_gspread_client()
    spreadsheet = client.open_by_key(config.EVENTS_SPREADSHEET_ID)
    sheet_names = [ws.title for ws in spreadsheet.worksheets()]

    all_data = {}

    for sheet_name in sheet_names:
        try:
            ws = spreadsheet.worksheet(sheet_name)
            records = ws.get_all_records()
            all_data[sheet_name] = records
        except Exception as e:
            print(f"[get_admin_all_data] error on {sheet_name}: {e}")

    return all_data

# 取消報名
def cancel_signup(sheet_name, line_name):
    try:
        client = init_gspread_client()
        sheet = client.open(sheet_name).sheet1
        records = sheet.get_all_records()
        for idx, record in enumerate(records):
            if record.get("LINE名稱") == line_name:
                sheet.delete_rows(idx + 2)  # 加2因為get_all_records略過表頭
                return True
        return False
    except Exception as e:
        print(f"[cancel_signup] error: {e}")
        return False
