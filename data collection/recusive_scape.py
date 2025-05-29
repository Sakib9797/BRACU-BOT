from playwright.sync_api import sync_playwright, TimeoutError
from urllib.parse import urlparse, urljoin
import os

def extract_text(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    return soup.get_text(separator=' ', strip=True)

def get_internal_links(page, base_url):
    base_domain = urlparse(base_url).netloc
    anchors = page.query_selector_all("a[href]")
    links = set()

    for a in anchors:
        href = a.get_attribute("href")
        if not href:
            continue
        absolute_url = urljoin(base_url, href)
        parsed = urlparse(absolute_url)
        if parsed.netloc == base_domain:
            clean_url = absolute_url.split('#')[0]
            links.add(clean_url)

    return links

def safe_filename(title, max_len=50):
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for c in invalid_chars:
        title = title.replace(c, '_')
    return title.strip().replace(' ', '_')[:max_len]

def scrape_recursive(start_url):
    visited = set()
    to_visit = [start_url]
    os.makedirs("scraped_pages", exist_ok=True)
    count = 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/100.0.4896.127 Safari/537.36",
            viewport={"width": 1280, "height": 720},
        )

        while to_visit:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)
            print(f"\nScraping: {url}")

            page = context.new_page()
            try:
                page.goto(url, wait_until="load", timeout=90000)
                page.wait_for_timeout(5000)  # wait 5 seconds more just in case

            except TimeoutError:
                print(f"Timeout at {url}. Continuing anyway.")
            except Exception as e:
                print(f"Error loading {url}: {e}")
                page.close()
                continue

            try:
                html = page.content()
                text = extract_text(html)
                title = page.title() or f"page{count}"
                filename = safe_filename(f"{count}_{title}")
                filepath = os.path.join("scraped_pages", f"{filename}.txt")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"Saved: {filepath}")
            except Exception as e:
                print(f"Error processing page: {e}")
            finally:
                new_links = get_internal_links(page, url)
                for link in new_links:
                    if link not in visited and link not in to_visit:
                        to_visit.append(link)
                page.close()
                count += 1

        browser.close()

if __name__ == "__main__":
    start_url = "https://www.bracu.ac.bd"
    scrape_recursive(start_url)
