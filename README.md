# BRACU Chatbot

A RAG (Retrieval-Augmented Generation) chatbot that answers questions about
**BRAC University** using content scraped from [bracu.ac.bd](https://www.bracu.ac.bd/).

- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`
- **Generator:** `google/flan-t5-base`
- **Vector store:** FAISS (IndexFlatL2)
- **UI:** Gradio `ChatInterface`

## Quick start

```powershell
# 1. Create a virtual environment (one time)
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. Run the bot
.\.venv\Scripts\python.exe app.py
```

Then open <http://127.0.0.1:7860> in your browser.

The first chat message triggers model downloads (~1 GB total) into your
HuggingFace cache (`%USERPROFILE%\.cache\huggingface`).

## Project layout

```
app.py                        # Gradio chat UI + RAG pipeline (entry point)
scrap_list.py                 # Simple URL-list scraper (writes to data/)
data/                         # Scraped corpus (text files, one per page)
data collection/
    scrape_via_api.py         # ScraperAPI-driven bulk scraper
    recusive_scape.py         # Playwright recursive scraper (Cloudflare-aware)
fetch_sitemap.py              # Pulls BRACU sitemap.xml → urls.json
filter_urls.py                # Filters sitemap → urls_filtered.json (67 pages)
smoke_test.py                 # Quick scraper smoke test
scrape_all.py                 # Convenience wrapper
requirements.txt              # Pinned dependencies
```

## Refreshing the corpus

The chatbot's knowledge comes from `.txt` files in `data/`. To rebuild it:

### Option A — ScraperAPI (recommended, handles Cloudflare for you)

```powershell
$env:SCRAPERAPI_KEY = "your-key-here"
.\.venv\Scripts\python.exe "data collection\scrape_via_api.py"
```

Free tier: 1000 requests/month, plenty for the 67 filtered pages.

### Option B — Local Playwright

```powershell
.\.venv\Scripts\python.exe "data collection\recusive_scape.py"
```

May be blocked by Cloudflare depending on your IP reputation.

After scraping, restart `app.py` — the FAISS index is rebuilt from `data/`
on startup.

## How it works

1. **Indexing** (on startup): every `.txt` in `data/` is split into
   ~800-character sentence-aware chunks, embedded with MiniLM, and stored
   in a FAISS index.
2. **Retrieval** (per question): the question is embedded, the top-5 most
   similar chunks are pulled from the index.
3. **Generation**: the chunks are stuffed into a small prompt and passed
   to FLAN-T5, which produces a short grounded answer.

## Notes & limitations

- The QA model is small (~250M params), so answers are short and
  sometimes imprecise on long questions. Swap `google/flan-t5-base` for
  `flan-t5-large` in `app.py` for noticeably better answers (4× slower).
- Cloudflare protections on bracu.ac.bd occasionally block the local
  scraper — use ScraperAPI if this happens.
- The current corpus is a small filtered subset. Expanding it (more
  pages, PDFs, faculty listings) is the highest-impact next step.

## License

MIT.