import os
from dotenv import load_dotenv

load_dotenv()  # 本地開發時才會讀 .env，在 Vercel 會自動讀系統變數

CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID")
EVENTS_SPREADSHEET_ID = os.environ.get("EVENTS_SPREADSHEET_ID")
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
