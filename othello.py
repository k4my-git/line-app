# 初期のオセロボードを設定
def initial_board():
    board = [['' for _ in range(8)] for _ in range(8)]
    board[3][3] = 'W'
    board[4][4] = 'W'
    board[3][4] = 'B'
    board[4][3] = 'B'
    return board

# 石を置けるか確認する関数
def is_valid_move(board, row, col, color):
    if board[row][col] != '':
        return False

    other_color = 'B' if color == 'W' else 'W'
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
    valid = False

    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < 8 and 0 <= c < 8 and board[r][c] == other_color:
            while 0 <= r < 8 and 0 <= c < 8:
                r += dr
                c += dc
                if r < 0 or r >= 8 or c < 0 or c >= 8 or board[r][c] == '':
                    break
                if board[r][c] == color:
                    valid = True
                    break

    return valid

# 石を置き、相手の石をひっくり返す関数
def place_stone(board, row, col, color):
    board[row][col] = color
    other_color = 'B' if color == 'W' else 'W'
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc
        stones_to_flip = []

        while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == other_color:
            stones_to_flip.append((r, c))
            r += dr
            c += dc

        if 0 <= r < 8 and 0 <= c < 8 and board[r][c] == color:
            for rr, cc in stones_to_flip:
                board[rr][cc] = color

# ゲーム終了判定
def is_game_over(board):
    for row in range(8):
        for col in range(8):
            if board[row][col] == '' and (is_valid_move(board, row, col, 'B') or is_valid_move(board, row, col, 'W')):
                return False
    return True

# スコア計算
def calculate_score(board):
    black_score = sum(row.count('B') for row in board)
    white_score = sum(row.count('W') for row in board)
    return black_score, white_score

# ボードをFlexメッセージに変換
def board_to_flex(board):
    contents = []
    for row in range(8):
        row_contents = []
        for col in range(8):
            cell = board[row][col]
            if cell == 'B':
                color = '#000000'
            elif cell == 'W':
                color = '#c0c0c0'
            else:
                color = '#008000'  # 空のセルは緑色
            row_contents.append({
                "type": "button",
                "action": {
                    "type": "postback",
                    "label": " ",
                    "data": f"move,{row},{col}"
                },
                "height": "sm",
                "style": "primary",
                "color": color
            })
        contents.append({
            "type": "box",
            "layout": "horizontal",
            "contents": row_contents
        })
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": contents
        }
    }