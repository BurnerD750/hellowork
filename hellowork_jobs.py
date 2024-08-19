import os
import logging
import asyncio
from dotenv import load_dotenv
from asyncpg import create_pool
from playwright.async_api import async_playwright
from fields import FIELDS
from login_handler import login
from datetime import datetime

start_time = datetime.now()

# .envファイルを読み込む
load_dotenv()

# 環境変数からデータベースの接続情報を取得
DATABASE_URL = os.getenv("DATABASE_URL")

logging.basicConfig(level=logging.INFO)

async def safe_find_text(page, selector, default_value=""):
    try:
        element = await page.query_selector(selector)
        if element:
            text = await element.text_content()
            return text.strip() if text else default_value
        else:
            return default_value
    except Exception as e:
        logging.error(f"Error occurred while finding text for selector {selector}: {e}")
        return default_value

async def save_url_to_db(conn, url):
    try:
        sql = '''
        INSERT INTO hw_jobs (url)
        VALUES ($1)
        ON CONFLICT (url) DO NOTHING;
        '''
        await conn.execute(sql, url)
    except Exception as e:
        logging.error(f"Error inserting URL {url} into db: {e}")

async def fetch_and_save_links(page, pool, context):
    page_number = 1
    while True:
        try:
            await page.wait_for_selector("#ID_dispDetailBtn")
            elements = await page.query_selector_all("#ID_dispDetailBtn")
            logging.info(f"Page {page_number}: Fetched {len(elements)} links on current page.")

            async with pool.acquire() as conn:
                async with conn.transaction():
                    for element in elements:
                        onclick = await element.get_attribute('onclick')
                        params = onclick.split("'")
                        job_id = params[1]
                        job_category = params[3]
                        company_id = params[5]
                        full_part = params[7]

                        link = (f'https://kyushoku.hellowork.mhlw.go.jp/kyushoku/GEAA110010.do?screenId=GEAA110010&action=dispDetailBtn'
                                f'&kJNo={job_id}&kJKbn={job_category}&jGSHNo={company_id}&fullPart={full_part}'
                                '&iNFTeikyoRiyoDtiID=&kSNo=&newArrived=&tatZngy=1&shogaiKbn=0')

                        await save_url_to_db(conn, link)

            next_button = await page.query_selector('input[name="fwListNaviBtnNext"]')
            if next_button:
                is_disabled = await next_button.get_attribute('disabled') is not None
                if not is_disabled:
                    logging.info("Next button found and enabled, moving to the next page.")
                    try:
                        await next_button.click()
                        await page.wait_for_load_state('networkidle')
                        page_number += 1
                    except Exception as e:
                        logging.error(f"Error clicking next button: {e}")
                        break
                else:
                    logging.info("Next button is disabled, proceeding to the next operation.")
                    await process_all_jobs(pool, context)
                    break
            else:
                logging.info("No next button found.")
                await process_all_jobs(pool, context)
                break

        except Exception as e:
            logging.error(f"Error during fetching links: {e}")
            break

async def update_job_data(conn, page, url, job_count, total_jobs):
    try:
        await page.goto(url)
        job_data = {"url": url}

        for field in FIELDS:
            selector = f'[class="m05"][name="{field}"][id="ID_{field}"]'
            value = await safe_find_text(page, selector)
            job_data[field] = value if value else ""    

        fields = list(job_data.keys())
        placeholders = [f'${i+1}' for i in range(len(fields))]
        updates = [f'"{field}" = EXCLUDED."{field}"' for field in fields if field != "url"]

        sql = f'''
        INSERT INTO hw_jobs ({", ".join(f'"{field}"' for field in fields)})
        VALUES ({", ".join(placeholders)})
        ON CONFLICT (url) DO UPDATE 
        SET {", ".join(f'"{field}" = EXCLUDED."{field}"' for field in fields if field != "url")}
        WHERE hw_jobs."kjNo" IS NULL;
        '''
        
        await conn.execute(sql, *job_data.values())

        end_time = datetime.now()
        elapsed_time = int((end_time - start_time).total_seconds())
        logging.info(f"{job_count}/{total_jobs} in {elapsed_time} sec")
        
    except Exception as e:
        logging.error(f"Error processing {url}: {e}")
    finally:
        await page.close()

async def process_all_jobs(pool, context):
    async with pool.acquire() as conn:
        urls = await conn.fetch("SELECT url FROM hw_jobs")
        semaphore = asyncio.Semaphore(10)

        total_jobs = len(urls)
        tasks = []
        job_count = 1

        for record in urls:
            url = record['url']
            tasks.append(process_job_with_page(conn, context, url, job_count, total_jobs, semaphore))
            job_count += 1

        await asyncio.gather(*tasks)

    logging.info(f"All jobs processed. Total: {total_jobs} jobs.")

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

        await fetch_and_save_links(page, pool, context)

        await browser.close()
        await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
