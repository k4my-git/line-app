import psycopg2
from psycopg2.extras import DictCursor
import os

# 環境変数から PostgreSQL の URI を取得
DATABASE_URL = os.environ.get("HEROKU_POSTGRESQL_BRONZE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def insert_values(table,column,values):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f'INSERT INTO {table} {column} VALUES {values}')
        conn.commit()