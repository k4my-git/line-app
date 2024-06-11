import os
import requests
from flask import Flask, request, abort, g
from models import database
import othello

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, PostbackEvent
)

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# othelloデータベースの初期化
database.init_db()

othello_chat_id = None
othello_start_check = []

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

def delete_message(message_id):
    url = f'https://api.line.me/v2/bot/message/{message_id}/delete'

    headers = {
        'Authorization': f'Bearer {YOUR_CHANNEL_ACCESS_TOKEN}'
    }

    response = requests.delete(url, headers=headers)
    return response

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    msg = event.message
    user_id = event.source.user_id
    group_id = event.source.group_id
    if event.message.mention is not None:
        print(othello_start_check)
        if group_id in othello_start_check:
            print('ok2')
            othello_start_check.remove(group_id)
            mentioned_users = event.message.mention.mentionees
            user = mentioned_users[0]
            board = othello.initial_board()
            database.save_game(group_id, user_id, user.user_id, board, 'B')
            flex_message = FlexSendMessage(alt_text="オセロ", contents=othello.board_to_flex(board))
            line_bot_api.reply_message(event.reply_token, flex_message)
    elif msg.text == 'test':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='ok'))
    elif msg.text == 'Gid':
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=group_id))
    elif msg.text == 'Mid':
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=user_id))
    elif msg.text == 'dbset':
        database.groups_insert_values(group_id,False)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='ok'))
    elif msg.text == "start":
        othello_start_check.append(group_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='オセロの対戦相手をメンションしてください\nあなたは黒、相手は白です\n先手は黒です'))

    elif msg.text == "continue":
        board, turn = database.load_game(group_id)
        if board:
            flex_message = FlexSendMessage(alt_text="オセロ", contents=othello.board_to_flex(board))
            line_bot_api.reply_message(event.reply_token, flex_message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="進行中のゲームがありません。「start」と入力してゲームを開始してください。"))

# ポストバックイベントの処理
@handler.add(PostbackEvent)
def handle_postback(event):
    group_id = event.source.group_id
    user_id = event.source.user_id
    b_user, w_user, board, turn = database.load_game(group_id)

    if turn == 'B':
        if user_id != b_user:
            return
    else:
        if user_id != w_user:
            return

    if not board:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="ゲームを開始するには「start」と入力してください。"))
        return

    data = event.postback.data
    if data.startswith("move"):
        _, row, col = data.split(",")
        row = int(row)
        col = int(col)
        
        if othello.is_valid_move(board, row, col, turn):
            othello.place_stone(board, row, col, turn)
            if othello.is_game_over(board):
                black_score, white_score = othello.calculate_score(board)
                result_message = f"ゲーム終了\n黒: {black_score}, 白: {white_score}\n"
                if black_score > white_score:
                    result_message += "黒の勝ちです"
                elif white_score > black_score:
                    result_message += "白の勝ちです"
                else:
                    result_message += "引き分けです"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result_message))
                database.delete_game(group_id)
            else:
                turn = 'W' if turn == 'B' else 'B'
                database.save_game(group_id, b_user, w_user, board, turn)
                flex_message = FlexSendMessage(alt_text="オセロ", contents=othello.board_to_flex(board))
                line_bot_api.reply_message(event.reply_token, flex_message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="無効な手です"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
