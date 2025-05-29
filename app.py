import gradio as gr
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
from transformers import pipeline

# Load embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load and chunk your .txt files
chunks = []
for file in os.listdir("data"):
    if file.endswith(".txt"):
        with open(os.path.join("data", file), "r", encoding="utf-8") as f:
            text = f.read()
            chunks += [text[i:i+500] for i in range(0, len(text), 500)]

# Create embeddings
embeddings = embed_model.encode(chunks)
index = faiss.IndexFlatL2(embeddings[0].shape[0])
index.add(np.array(embeddings))

# Load small model for generation (fit for Spaces)
qa = pipeline("text2text-generation", model="google/flan-t5-base")


# RAG function
def rag_chat(query):
    query_vec = embed_model.encode([query])
    _, I = index.search(np.array(query_vec), k=3)
    context = "\n".join([chunks[i] for i in I[0]])
    prompt = f"Answer based on the context below:\n{context}\n\nQuestion: {query}\nAnswer:"
    out = qa(prompt, max_new_tokens=100, do_sample=True, temperature=0.7)[0]['generated_text']
    return out.split("Answer:")[-1].strip()

# Gradio UI
gr.Interface(fn=rag_chat, inputs="text", outputs="text", title="BRACU Chatbot").launch()
