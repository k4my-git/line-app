import os
from flask import Flask, request, abort, g
import psycopg2

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
#DATABASE_URL = os.environ.get("DATABASE_URL")


#def get_pg_conn():
#    """ PostgreSQL へ接続 """
#    if not hasattr(g, "pg_conn"):
#        g.pg_conn = psycopg2.connect(DATABASE_URL)
#    return g.pg_conn
#
#
#@app.teardown_appcontext
#def close_pg_conn(error):
#    """ エラーが発生したら PostgreSQL への接続を閉じる """
#    if hasattr(g, "pg_conn"):
#        g.pg_conn.close()

@app.route("/")
def hello_world():
    #conn = get_pg_conn()
    #cursor = conn.cursor()
    return "hello world!"

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
    if msg.text == 'test':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='ok'))

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
