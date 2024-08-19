import sqlite3
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

# 環境変数からデータベースのパスを取得
database_path = os.getenv("DATABASE_PATH")

# データベースに接続
conn = sqlite3.connect(database_path, check_same_thread=False)
cursor = conn.cursor()

# memo.html の絶対パスを取得
file_path = os.path.join(os.path.dirname(__file__), 'memo.html')

# ファイルを開く
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        html_data = file.read()
except FileNotFoundError:
    print(f"Error: {file_path} not found.")
    conn.close()
    exit(1)

# BeautifulSoupでHTMLを解析
soup = BeautifulSoup(html_data, 'html.parser')

# URLを仮定して取得
url = "https://example.com/job_detail"

# classがm05のすべてのdivタグのid属性を取得し、テーブル作成用のカラムリストを作成
columns = ["url"]  # 先頭にURLカラムを追加
data = [url]  # データリストの先頭にURLを追加
for div in soup.find_all('div', class_='m05'):
    div_name = div.get('name')
    if div_name:
        columns.append(div_name)
        data.append(div.get_text(strip=True))

# テーブルを動的に作成
table_name = "hw_jobs"
columns_sql = "id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE, " + ", ".join([f"{col} TEXT" for col in columns[1:]])

try:
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})")
except sqlite3.Error as e:
    print(f"An error occurred while creating the table: {e}")
    conn.close()
    exit(1)

try:
    # URLがすでに存在するかを確認
    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE url = ?", (url,))
    if cursor.fetchone()[0] > 0:
        # 存在する場合はUPDATE
        update_sql = ", ".join([f"{col} = ?" for col in columns[1:]])
        cursor.execute(f"UPDATE {table_name} SET {update_sql} WHERE url = ?", data[1:] + [url])
        print("Data has been updated in the hw_jobs table.")
    else:
        # 存在しない場合はINSERT
        placeholders = ", ".join(["?"] * len(columns))
        cursor.execute(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})", data)
        print("Data has been inserted into the hw_jobs table.")

    # コミットして接続を閉じる
    conn.commit()

except sqlite3.Error as e:
    print(f"An error occurred while inserting/updating the data: {e}")
finally:
    conn.close()
