# app.py

from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "✅ LINE Bot Flask Server is running on Vercel!"

# 這段是 Vercel 要求的 entry point（確保有變數 app）
# 不需要寫 app.run()，Vercel 自動處理啟動
