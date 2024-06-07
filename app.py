import os
from flask import Flask, request, abort, g
import psycopg2
from psycopg2.extras import DictCursor

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# 環境変数から PostgreSQL の URI を取得
DATABASE_URL = os.environ.get("HEROKU_POSTGRESQL_BRONZE_URL")

@app.route("/")
def hello_world():
    return "hello world!"

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message
    user_id = event.source.user_id
    if msg.text == 'test':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='ok'))
    elif msg.text == 'dbset':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='ok'))

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
