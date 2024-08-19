from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from job_data_extractor import extract_and_save_job_data  # 既存の関数をインポート
from login_handler import login
import sqlite3
import os
import time
from dotenv import load_dotenv
from threading import Lock
import asyncio

# .envファイルを読み込む
load_dotenv()

# 環境変数からデータベースのパスを取得
database_path = os.getenv("DATABASE_PATH")

# データベースに接続
conn = sqlite3.connect(database_path, check_same_thread=False)
cursor = conn.cursor()

# ブラウザの数を設定
NUM_BROWSERS = 5

# ヘッドレスモードのChromeオプションを設定
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--disable-software-rasterizer')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument('--disable-popup-blocking')
chrome_options.add_argument('--disable-logging')
chrome_options.add_argument('--mute-audio')
chrome_options.add_argument('--disable-background-networking')
chrome_options.add_argument('--disable-background-timer-throttling')
chrome_options.add_argument('--disable-backgrounding-occluded-windows')
chrome_options.add_argument('--disable-renderer-backgrounding')
chrome_options.add_argument('--no-zygote')
chrome_options.add_argument('--incognito')

# NUM_BROWSERS個のWebDriverインスタンスとロックの作成
drivers = [webdriver.Chrome(options=chrome_options) for _ in range(NUM_BROWSERS)]
driver_locks = [Lock() for _ in range(NUM_BROWSERS)]

def safe_find_text(driver, selector, by=By.CSS_SELECTOR, default_value="default_value"):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((by, selector))
        )
        return element.text.strip() if element else default_value
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error occurred while finding text: {e}")
        return default_value

def fetch_all_links(driver):
    all_links = []
    while True:
        elements = driver.find_elements(By.CSS_SELECTOR, "#ID_dispDetailBtn")
        for element in elements:
            onclick = element.get_attribute('onclick')
            params = onclick.split("'")
            job_id = params[1]
            job_category = params[3]
            company_id = params[5]
            full_part = params[7]

            link = (f'https://kyushoku.hellowork.mhlw.go.jp/kyushoku/GEAA110010.do?screenId=GEAA110010&action=dispDetailBtn'
                    f'&kJNo={job_id}&kJKbn={job_category}&jGSHNo={company_id}&fullPart={full_part}'
                    '&iNFTeikyoRiyoDtiID=&kSNo=&newArrived=&tatZngy=1&shogaiKbn=0')
            all_links.append(link)

        try:
            next_button = driver.find_element(By.NAME, "fwListNaviBtnNext")
            if next_button.is_enabled():
                next_button.click()
                time.sleep(1)
            else:
                print("次へボタンが無効化されていますか、見つかりません。終了します。")
                break
        except:
            print("次へボタンが見つかりません。終了します。")
            break

    return all_links

async def process_page(url, cursor, driver, driver_lock):
    retries = 0
    max_retries = 10
    
    while retries < max_retries:
        try:
            with driver_lock:
                print(f"Processing {url}")
                extract_and_save_job_data(cursor, driver, url)
                print(f"Successfully processed {url}")
            break
        except Exception as e:
            retries += 1
            print(f"Failed to process page {url} (Attempt {retries}/{max_retries}): {e}")
            await asyncio.sleep(5 * retries)

    if retries == max_retries:
        print(f"Skipping {url} after {max_retries} failed attempts")

async def main():
    for driver in drivers:
        login(driver)

    all_links = fetch_all_links(drivers[0])

    tasks = [
        process_page(url, cursor, drivers[i % NUM_BROWSERS], driver_locks[i % NUM_BROWSERS])
        for i, url in enumerate(all_links)
    ]

    await asyncio.gather(*tasks)

    for driver in drivers:
        driver.quit()

    conn.close()

if __name__ == "__main__":
    asyncio.run(main())
