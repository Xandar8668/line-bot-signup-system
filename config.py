# config.py

import os

# 從環境變數讀取 LINE 機器人金鑰
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")

# 管理員 LINE ID
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID")

# Google Sheets 活動清單表格 ID
EVENTS_SPREADSHEET_ID = os.environ.get("EVENTS_SPREADSHEET_ID")

# credentials JSON 將在 sheets.py 處理
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
