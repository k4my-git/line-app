import os
import time
import pytz
import threading
from datetime import datetime
from flask import Flask, request, abort, g
from models import database

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


@app.route("/")
def hello_world():
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
    print(event)
    msg = event.message
    user_id = event.source.user_id
    group_id = event.source.group_id
    if msg.text == 'test':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='ok'))
    elif msg.text == 'dbset':
        database.groups_insert_values(group_id,False)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='ok'))

def send_uranai():
    print('schedule')
    to = 'Cd4be544e806ee37f624dfe92d68d6267'
    message = TextSendMessage(text='uranai')
    line_bot_api.push_message(to, message)


def schedule_loop():
    while True:
        now = datetime.now(pytz.timezone('Asia/Tokyo'))
        current_time = now.strftime("%H:%M:%S")
        print(current_time)
        if "17:10:00" <= current_time <= "17:10:1":
            send_uranai()
        time.sleep(1)

if __name__ == "__main__":
    thread1 = threading.Thread(target=schedule_loop)
    thread1.start()
    print("Thread has started.")
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
