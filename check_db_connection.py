import os
import psycopg2
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からDATABASE_URLを取得
database_url = os.getenv("DATABASE_URL")

# データベース接続のテスト
try:
    # データベースに接続
    conn = psycopg2.connect(database_url)
    # カーソルを作成
    cursor = conn.cursor()
    
    # 接続が成功した場合のメッセージ
    print("Database connection successful")
    
    # 簡単なクエリを実行してみる（例：テーブル一覧を取得）
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cursor.fetchall()
    
    # テーブル一覧を表示
    print("Tables in the database:")
    for table in tables:
        print(table[0])
    
    # カーソルと接続を閉じる
    cursor.close()
    conn.close()

except Exception as e:
    # 接続が失敗した場合のメッセージ
    print(f"Database connection failed: {e}")
