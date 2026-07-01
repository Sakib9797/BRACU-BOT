from playwright.sync_api import sync_playwright, TimeoutError
import os
import re

def scrape_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headful to see browser window
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/100.0.4896.127 Safari/537.36",
            viewport={"width": 1280, "height": 720},
        )
        page = context.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
        except TimeoutError:
            print(f"Timeout while loading {url}. Proceeding with partial content.")
        content = page.content()
        browser.close()
        return content

def extract_text_and_title(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    title = soup.title.string.strip() if soup.title else "no_title"
    text = soup.get_text(separator=' ', strip=True)
    return text, title


def sanitize_filename(name):
    name = re.sub(r'[^\w\s-]', '', name)  # remove illegal characters
    name = re.sub(r'[\s]+', '_', name)    # replace spaces with underscores
    return name[:100]  # truncate to avoid long filenames


if __name__ == "__main__":
    url = "....."  # Change this URL manually for other pages
    page_num = 2  # Change this to increment for saving multiple pages
    
    html = scrape_with_playwright(url)
    text, title = extract_text_and_title(html)
    safe_title = sanitize_filename(title)
    
    # Create folder if not exists
    os.makedirs("scraped_pages", exist_ok=True)
    
    file_path = f"scraped_pages/{page_num}_{safe_title}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"Scraped text saved to {file_path}")
    print(text[:500])  # Print first 500 chars of cleaned text
