from playwright.sync_api import sync_playwright, TimeoutError
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import re

HEADFUL = os.environ.get("HEADFUL", "0") == "1"
DATA_DIR = "data"

def scrape_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not HEADFUL)
        context = browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"),
            viewport={"width": 1280, "height": 720},
        )
        page = context.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
        except TimeoutError:
            print(f"Timeout while loading {url}. Proceeding with partial content.")
        html = page.content()
        browser.close()
        return html

def extract_text_and_title(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()
    title = (soup.title.string or "").strip() if soup.title else ""
    text = soup.get_text(separator=' ', strip=True)
    text = re.sub(r'\s+', ' ', text).strip()
    return text, title

def sanitize_filename(name, max_len=80):
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', '_', name).strip('_')
    return name[:max_len] or "untitled"

def url_slug(url):
    path = urlparse(url).path.strip('/').replace('/', '_')
    return sanitize_filename(path) or "home"

if __name__ == "__main__":
    urls = [
        "https://www.bracu.ac.bd",
        "https://www.bracu.ac.bd/admissions/apply-now",
    ]

    os.makedirs(DATA_DIR, exist_ok=True)

    for i, url in enumerate(urls, start=1):
        print(f"Scraping {url}")
        html = scrape_with_playwright(url)
        text, title = extract_text_and_title(html)

        slug = url_slug(url)
        file_path = os.path.join(DATA_DIR, f"{i}_{slug}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Saved scraped text to {file_path} (title={title!r})")
        print(text[:500])
