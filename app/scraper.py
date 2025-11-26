import re
import asyncio
from urllib.parse import urlparse, urljoin
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from redis import Redis
import logging

logging.basicConfig(level=logging.INFO)

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
MAX_PAGES = 10
PAGE_TIMEOUT = 15000  # 15 seconds
RETRIES = 2
CONCURRENCY = 3       # Pages scraped concurrently
CACHE_TTL = 86400     # 24 hours cache

redis_conn = Redis(host="redis", port=6379)

def extract_emails(text):
    return set(re.findall(EMAIL_REGEX, text))

def filter_internal_links(base_url, links, seen):
    parsed_base = urlparse(base_url)
    internal = []
    for link in links:
        parsed = urlparse(link)
        if parsed.netloc == parsed_base.netloc and link not in seen:
            internal.append(link)
    return internal

async def fetch_page_content(page, url):
    for attempt in range(RETRIES):
        try:
            await page.goto(url, timeout=PAGE_TIMEOUT)
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            links = [urljoin(url, a.get('href')) for a in soup.find_all('a', href=True)]
            return soup.get_text(separator=" ", strip=True), links
        except PlaywrightTimeoutError:
            logging.warning(f"Timeout loading {url}, attempt {attempt+1}/{RETRIES}")
        except Exception as e:
            logging.warning(f"Error fetching {url}: {e}")
    return "", []

async def scrape_worker(url, browser, visited, to_visit, emails, semaphore):
    async with semaphore:
        if url in visited or len(visited) >= MAX_PAGES:
            return
        visited.add(url)
        page = await browser.new_page()
        logging.info(f"Crawling {url}")
        text, links = await fetch_page_content(page, url)
        emails.update(extract_emails(text))
        await page.close()
        # Add new internal links if under max pages
        new_links = filter_internal_links(url, links, visited)
        for link in new_links:
            if len(visited) + len(to_visit) < MAX_PAGES:
                to_visit.append(link)

async def _scrape_site_async(url, job_id):
    # Check cache first
    cached = redis_conn.get(f"CACHE:{url}")
    if cached:
        logging.info(f"Cache hit for {url}")
        redis_conn.set(job_id, cached, ex=CACHE_TTL)  # Update job with cached result
        return

    visited = set()
    to_visit = [url]
    emails = set()
    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        while to_visit and len(visited) < MAX_PAGES:
            batch = to_visit[:CONCURRENCY]
            to_visit = to_visit[CONCURRENCY:]
            tasks = [scrape_worker(u, browser, visited, to_visit, emails, semaphore) for u in batch]
            await asyncio.gather(*tasks)

        await browser.close()

    result = str(list(emails))
    # Save to Redis with TTL
    redis_conn.set(job_id, result, ex=CACHE_TTL)
    redis_conn.set(f"CACHE:{url}", result, ex=CACHE_TTL)
    logging.info(f"Scraping complete for {url}, found {len(emails)} emails, cached for {CACHE_TTL}s")

def scrape_site(url, job_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_scrape_site_async(url, job_id))
