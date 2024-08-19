from dotenv import load_dotenv
import os
import pickle
from playwright.async_api import async_playwright
import asyncio
import logging

# .envファイルを読み込む
load_dotenv()

# ログ設定
logging.basicConfig(level=logging.INFO)

# 環境変数からログイン情報を取得
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

async def login(page):
    url = 'https://kyushoku.hellowork.mhlw.go.jp/kyushoku/GEAA040010.do?action=initDisp&screenId=GEAA040010'
    await page.goto(url)

    # Emailとパスワードを入力してログイン
    await page.fill('#ID_loginMailTxt', email)
    await page.fill('#ID_loginPasswordTxt', password)
    await page.click('#ID_loginBtn')

    await page.wait_for_selector('#ID_searchBtn')

    # 「検索」ボタンをクリック
    search_buttons = await page.query_selector_all('#ID_searchBtn')
    if len(search_buttons) > 1:
        await retry_click(search_buttons[1])
    else:
        logging.error("Search buttons not found or not enough buttons.")

    await page.wait_for_selector('#ID_fwListNaviDispTop')

    # 表示件数を50件に変更
    select_element = await page.query_selector('#ID_fwListNaviDispTop')
    if select_element:
        await select_element.select_option(value='50')

        # Enterキーを押す
        await page.keyboard.press('Enter')
        logging.info("Enter key pressed after selecting 50 items per page.")

        # URLが変わってもページ遷移を待つ
        await page.wait_for_load_state('networkidle')

        # 5秒待機
        logging.info("Waiting for 5 seconds...")
        await page.wait_for_timeout(5000)
        logging.info("5 seconds wait completed.")
    else:
        logging.error("Select element not found.")

    # クッキーを保存
    cookies = await page.context.cookies()
    with open("cookies.pkl", "wb") as f:
        pickle.dump(cookies, f)

async def retry_click(option, retries=3):
    for attempt in range(retries):
        try:
            visible = await option.is_visible()
            if not visible:
                logging.warning(f"Option is not visible, attempting to scroll into view (Attempt {attempt+1}).")
                await option.scroll_into_view_if_needed(timeout=10000)
            await option.click(force=True)
            return
        except Exception as e:
            logging.error(f"Click attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(2)
                continue
            else:
                raise e

# Playwrightのエントリーポイント
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await login(page)
        await page.wait_for_timeout(5000)  # 5秒待機してからブラウザを閉じる
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
