import psycopg2
from hellowork_jobs import update_job_data

# PostgreSQLデータベースに接続
conn = psycopg2.connect(
    dbname="your_database_name",
    user="your_username",
    password="your_password",
    host="your_host",
    port="your_port"
)

# カーソルを作成
cur = conn.cursor()

# kjNoがNULLのレコードのURLを取得
cur.execute("SELECT url FROM hw_jobs WHERE kjNo IS NULL;")
urls = cur.fetchall()

# 各URLでupdate_job_dataを実行
for url in urls:
    update_job_data(url[0])

# カーソルと接続を閉じる
cur.close()
conn.close()
