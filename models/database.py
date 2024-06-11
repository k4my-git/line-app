import psycopg2
from psycopg2.extras import DictCursor
import os
import json

# 環境変数から PostgreSQL の URI を取得
DATABASE_URL = os.environ.get("HEROKU_POSTGRESQL_BRONZE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def groups_insert_values(gid, uranai):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f'INSERT INTO groups (gid, uranai) VALUES (%s, %s)', (gid,uranai))
        conn.commit()

#othello DB
def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    group_id text not null,
                    B_user_id text,
                    W_user_id text,
                    board text,
                    turn text,
                    constraint games_pk PRIMARY KEY(group_id)
                )
            ''')
        conn.commit()

def save_game(user_id,b_user_id, w_user_id, board, turn):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO games (group_id, B_user_id, W_user_id, board, turn) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE
                SET B_user_id = EXCLUDED.B_user_id, W_user_id = EXCLUDED.W_user_id, board = EXCLUDED.board, turn = EXCLUDED.turn
            ''', (user_id, b_user_id, w_user_id, json.dumps(board), turn))
        conn.commit()

def load_game(group_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT B_user_id, W_user_id, board, turn FROM games WHERE group_id = %s', (group_id,))
            row = cur.fetchone()
        if row:
            return row[0], row[1], json.loads(row[2]), row[3]
        return None, None, None, None

def delete_game(group_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM games WHERE group_id = %s', (group_id,))
        conn.commit()
