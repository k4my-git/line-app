from flask import Flask, request, abort
import os

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

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)

def main():
    to = 'Cd4be544e806ee37f624dfe92d68d6267'
    pushText = TextSendMessage(text="schedule")
    line_bot_api.push_message(to, messages=pushText)

if __name__ == "__main__":
    main()