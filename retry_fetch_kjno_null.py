import os
import logging
import asyncio
from dotenv import load_dotenv
from asyncpg import create_pool
from playwright.async_api import async_playwright
from login_handler import login
from datetime import datetime
from hellowork_jobs import update_job_data

# ログの設定
logging.basicConfig(level=logging.INFO)

# .envファイルを読み込む
load_dotenv()

# 環境変数からデータベースの接続情報を取得
DATABASE_URL = os.getenv("DATABASE_URL")

async def fetch_null_kjno_urls(conn):
    try:
        sql = 'SELECT url FROM hw_jobs WHERE "kjNo" IS NULL;'
        urls = await conn.fetch(sql)
        return [record['url'] for record in urls]
    except Exception as e:
        logging.error(f"Error fetching URLs with null kjNo: {e}")
        return []

async def retry_update_job_data(pool, context, max_retries=5):
    retry_count = 0

    while retry_count < max_retries:
        async with pool.acquire() as conn:
            urls = await fetch_null_kjno_urls(conn)

            if not urls:
                logging.info(f"No URLs found with null kjNo after {retry_count} retries.")
                break

            total_jobs = len(urls)
            semaphore = asyncio.Semaphore(10)
            tasks = []
            job_count = 1

            for url in urls:
                tasks.append(process_job_with_page(conn, context, url, job_count, total_jobs, semaphore))
                job_count += 1

            await asyncio.gather(*tasks)
            logging.info(f"Retry {retry_count + 1}/{max_retries} completed. Re-fetched {total_jobs} jobs with null kjNo.")

        retry_count += 1

        # 再確認
        async with pool.acquire() as conn:
            remaining_nulls = await fetch_null_kjno_urls(conn)
            if not remaining_nulls:
                logging.info("All jobs successfully updated. No null kjNo remains.")
                break

    if retry_count == max_retries:
        logging.info(f"Reached maximum retries ({max_retries}). Some jobs may still have null kjNo.")

async def process_job_with_page(conn, context, url, job_count, total_jobs, semaphore):
    async with semaphore:
        page = await context.new_page()
        try:
            await update_job_data(conn, page, url, job_count, total_jobs)
        finally:
            await page.close()

async def main():
    load_dotenv()

    try:
        pool = await create_pool(DATABASE_URL)
    except Exception as e:
        logging.error(f"Failed to create PostgreSQL pool: {e}")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        page = await context.new_page()
        await login(page)

        await retry_update_job_data(pool, context)

        await browser.close()
        await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
