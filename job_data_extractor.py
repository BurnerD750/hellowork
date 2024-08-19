from playwright.async_api import async_playwright
import sqlite3
import asyncio
from fields import FIELDS  # フィールドリストが定義されたファイルからインポート

async def safe_find_text(page, selector, default_value=""):
    try:
        element = await page.query_selector(selector)
        if element:
            text = await element.text_content()
            return text.strip() if text else default_value
        else:
            return default_value
    except Exception as e:
        # エラー発生時の処理
        return default_value

async def extract_and_save_job_data(conn, page, url):
    try:
        await page.goto(url)
        job_data = {"url": url}

        for field in FIELDS:
            selector = f'[name="{field}"]'
            job_data[field] = await safe_find_text(page, selector)

        sql = '''
        INSERT INTO hw_jobs ({fields})
        VALUES ({placeholders})
        ON CONFLICT ("url") DO UPDATE SET {updates}
        '''.format(
            fields=", ".join(f'"{field}"' for field in FIELDS),
            placeholders=", ".join(f':{field}' for field in FIELDS),
            updates=", ".join(f'"{field}" = EXCLUDED."{field}"' for field in FIELDS)
        )

        await conn.execute(sql, job_data)
        await conn.commit()
        print(f"Data inserted for {url}")

    except Exception as e:
        print(f"Error processing {url}: {e}")

