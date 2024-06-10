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
                    user_id text not null,
                    board text,
                    turn text,
                    constraint games_pk PRIMARY KEY(user_id)
                )
            ''')
        conn.commit()

def save_game(user_id, board, turn):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO games (user_id, board, turn) VALUES (%s, %s, %s) on conflict on constraint games_pk do update set (user_id, board, turn) = (%s, %s, %s)', (user_id, json.dumps(board), turn, user_id, json.dumps(board), turn))
        conn.commit()

def load_game(user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT board, turn FROM games WHERE user_id = %s', (user_id,))
            row = cur.fetchone()
        if row:
            return json.loads(row[0]), row[1]
        return None, None

def delete_game(user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM games WHERE user_id = %s', (user_id,))
        conn.commit()
