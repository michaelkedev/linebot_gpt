from __future__ import unicode_literals
import os
import openai

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError

from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)


config = configparser.ConfigParser()
config.read("config.ini")
# LINE 聊天機器人的基本資料
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))

openai.api_key = os.getenv("OPENAI_API_KEY")

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 學你說話
@handler.add(MessageEvent, message=TextMessage)
def echo(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=event.message.text,
            max_tokens=128,
            temperature=0.5,
        )
        print(response["choices"][0]["text"])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text= response["choices"][0]["text"])
        )

if __name__ == "__main__":
    app.run()