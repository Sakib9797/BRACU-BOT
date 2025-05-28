from playwright.sync_api import sync_playwright, TimeoutError
import os

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

def extract_text(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    return soup.get_text(separator=' ', strip=True)

if __name__ == "__main__":
    urls = [
        "https://www.bracu.ac.bd",
        "https://www.bracu.ac.bd/admissions/apply-now",
    ]
    
    os.makedirs("scraped_pages", exist_ok=True)
    
    for i, url in enumerate(urls, start=1):
        print(f"Scraping {url}")
        html = scrape_with_playwright(url)
        text = extract_text(html)
        
        file_path = f"scraped_pages/page{i}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        print(f"Saved scraped text to {file_path}")
        print(text[:500])  # print preview
