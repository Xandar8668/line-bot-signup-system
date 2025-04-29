# reminder.py

import json
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
import requests
import config

# 初始化 Google Sheets
service_account_info = json.loads(config.GOOGLE_CREDENTIALS_JSON)
credentials = Credentials.from_service_account_info(service_account_info)
gc = gspread.authorize(credentials)

# LINE 推播功能（推播訊息到用戶）
def push_line_message(user_id, message):
    headers = {
        "Authorization": f"Bearer {config.CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "to": user_id,
        "messages": [{
            "type": "text",
            "text": message
        }]
    }
    r = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=data)
    print(f"Pushed to {user_id}: {r.status_code}")

# 主提醒函式
def remind_upcoming_events():
    sh = gc.open_by_key(config.EVENTS_SPREADSHEET_ID)
    event_list_ws = sh.worksheet("活動清單")
    event_list = event_list_ws.get_all_records()

    today = datetime.now().date()
    target_date = today + timedelta(days=2)

    reminders_sent = 0

    for event in event_list:
        event_date = datetime.strptime(event["日期"], "%Y-%m-%d").date()
        if event_date == target_date:
            sheet_name = event["活動名稱"]
            try:
                ws = sh.worksheet(sheet_name)
                records = ws.get_all_records()
                for row in records:
                    user_id = row.get("LINE名稱")  # 這欄要填 LINE 使用者 ID
                    if user_id:
                        msg = f"📣 提醒你：{sheet_name} 將於 {event['日期']} {event['時段']} 舉行，請準時集合！"
                        push_line_message(user_id, msg)
                        reminders_sent += 1
            except Exception as e:
                print(f"提醒失敗：{sheet_name}, 錯誤：{e}")
    return reminders_sent
