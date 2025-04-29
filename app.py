# app.py

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import config
import sheets

app = Flask(__name__)

line_bot_api = LineBotApi(config.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.CHANNEL_SECRET)

# Webhook 接收路由
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 根目錄
@app.route("/", methods=['GET'])
def index():
    return "✅ LINE Bot Flask Server is running!"

# 處理收到的文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    # 記錄用戶上一次的動作（簡易狀態機，這邊先略）
    
    if text == "我要報名":
        event_list = sheets.get_event_list()
        reply_text = "📋 可報名活動：\n"
        for idx, event_data in enumerate(event_list, 1):
            reply_text += f"{idx}. {event_data['活動名稱']}（{event_data['日期']} {event_data['時段']}）\n"
        reply_text += "\n請輸入報名資訊：\n活動名稱, 姓名, 電話, 人數, 備註"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

    elif text == "取消報名":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入取消報名資訊：\n取消活動名稱, LINE名稱")
        )

    elif text == "查詢我的報名":
        joined_events = sheets.get_user_signups(user_id)
        if joined_events:
            reply_text = "📖 你已報名的活動：\n" + "\n".join(joined_events)
        else:
            reply_text = "❗️ 查無你的報名紀錄"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

    elif text == "管理員查詢":
        if user_id == config.ADMIN_USER_ID:
            all_data = sheets.get_admin_all_data()
            reply_text = "🛡 管理員報名資料統計：\n"
            for sheet_name, records in all_data.items():
                reply_text += f"\n{sheet_name}: {len(records)} 人"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="你沒有管理員權限。")
            )

    elif "," in text:
        # 使用者輸入報名或取消指令
        fields = [f.strip() for f in text.split(",")]

        if len(fields) == 5:
            # 報名
            sheet_name, name, phone, number, note = fields
            success = sheets.add_signup(sheet_name, name, user_id, phone, number, note)
            if success:
                reply_text = "✅ 報名成功！"
            else:
                reply_text = "❌ 報名失敗，請稍後再試。"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )

        elif len(fields) == 2 and fields[0].startswith("取消"):
            # 取消報名
            sheet_name = fields[0].replace("取消", "").strip()
            line_name = fields[1]
            success = sheets.cancel_signup(sheet_name, line_name)
            if success:
                reply_text = "✅ 已取消報名"
            else:
                reply_text = "❌ 取消失敗，請確認資料是否正確。"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )

        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="❗️ 格式錯誤，請重新輸入。")
            )

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請使用指令：我要報名 / 取消報名 / 查詢我的報名 / 管理員查詢")
        )
from reminder import remind_upcoming_events

@app.route("/remind", methods=["GET"])
def remind():
    count = remind_upcoming_events()
    return f"✅ Reminders sent: {count}"
