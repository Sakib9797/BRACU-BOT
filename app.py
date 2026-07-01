import os
import re
import gradio as gr
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

DATA_DIR = "data"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
QA_MODEL_NAME = "google/flan-t5-base"

CHUNK_CHARS = 800      # ~ a few sentences
CHUNK_OVERLAP = 150    # overlap so a sentence split across chunks stays retrievable
TOP_K = 5

# --- Load embedding model ---
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

# --- Sentence-aware chunker (no mid-sentence breaks, with overlap) ---
_SENT_SPLIT = re.compile(r'(?<=[\.\?\!])\s+')

def split_sentences(text):
    text = text.strip()
    if not text:
        return []
    return [s.strip() for s in _SENT_SPLIT.split(text) if s.strip()]

def chunk_text(text, size=CHUNK_CHARS, overlap=CHUNK_OVERLAP):
    sentences = split_sentences(text)
    if not sentences:
        return []
    chunks = []
    buf = ""
    for sent in sentences:
        # if adding this sentence overflows, flush current buffer
        if buf and len(buf) + 1 + len(sent) > size:
            chunks.append(buf.strip())
            # build overlap tail from end of current chunk
            tail = buf[-overlap:] if overlap > 0 else ""
            buf = (tail + " " + sent).strip()
        else:
            buf = (buf + " " + sent).strip() if buf else sent
    if buf:
        chunks.append(buf.strip())
    return chunks

# --- Load docs and build index ---
sources = []      # parallel to embeddings: list of (filename, chunk_text)
for fname in sorted(os.listdir(DATA_DIR)):
    if not fname.endswith(".txt"):
        continue
    path = os.path.join(DATA_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    for chunk in chunk_text(text):
        if chunk:
            sources.append((fname, chunk))

if not sources:
    raise SystemExit(
        f"No chunks found in {DATA_DIR!r}. Run scrap_list.py first or drop .txt files in there."
    )

chunks = [c for _, c in sources]
embeddings = embed_model.encode(chunks, show_progress_bar=True, convert_to_numpy=True)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))

print(f"Indexed {len(chunks)} chunks from {len({f for f, _ in sources})} file(s).")

# --- Load QA model ---
qa_tokenizer = AutoTokenizer.from_pretrained(QA_MODEL_NAME)
qa_model = AutoModelForSeq2SeqLM.from_pretrained(QA_MODEL_NAME)
qa_model.eval()
qa_device = "cuda" if torch.cuda.is_available() else "cpu"
qa_model.to(qa_device)

# --- RAG function ---
SYSTEM_INSTRUCTION = (
    "Answer the question using only the context. "
    "If the answer is not in the context, reply exactly: I don't have that information."
)

NO_ANSWER = "I don't have that information."

# flan-t5-base input window is 512 tokens; longer prompts make it start
# "continuing" the context instead of answering.
MAX_CONTEXT_CHARS = 1800
MAX_INPUT_TOKENS = 512

def _trim(retrieved, max_chars=MAX_CONTEXT_CHARS):
    out, total = [], 0
    for c in retrieved:
        if out and total + len(c) > max_chars:
            break
        out.append(c)
        total += len(c)
    return out

def _format_prompt(context, query):
    # flan-t5 works best with short, direct instructions; question right
    # before the answer, no extra "Answer:" prompt to confuse it.
    return (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"Context: {context}\n\n"
        f"Question: {query}"
    )

def rag_chat(query, history=None):
    if not query or not query.strip():
        return "Please ask a question."

    query_vec = embed_model.encode([query], convert_to_numpy=True)
    _, I = index.search(np.array(query_vec), k=TOP_K)

    retrieved = _trim([chunks[i] for i in I[0] if i < len(chunks)])
    context = " ".join(retrieved)

    prompt = _format_prompt(context, query)

    inputs = qa_tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_INPUT_TOKENS,
    ).to(qa_device)

    with torch.no_grad():
        output_ids = qa_model.generate(
            **inputs,
            max_new_tokens=120,        # flan-t5-base sweet spot
            min_new_tokens=4,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=3,    # stop copying phrases verbatim
        )

    answer = qa_tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

    lowered = answer.lower()
    if not answer or lowered.startswith(("i don't", "i do not", "i'm not sure", "i am not sure", "i cannot")):
        return NO_ANSWER
    return answer

if __name__ == "__main__":
    gr.ChatInterface(
        fn=rag_chat,
        title="BRACU Chatbot",
        description="Ask questions about BRAC University. Answers are grounded in the scraped site content.",
    ).launch()
