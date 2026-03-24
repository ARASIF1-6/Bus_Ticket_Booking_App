import os, json
from typing import List
from pathlib import Path

DATA_JSON = os.getenv("DATA_JSON_PATH", "/data/data.json")
SHYAMOLI_PATH = os.getenv("SHYAMOLI_PATH", "/data/shyamoli.txt")
SOUDIA_PATH = os.getenv("SOUDIA_PATH", "/data/soudia.txt")

def load_documents():
    docs = []
    # data.json
    if os.path.exists(DATA_JSON):
        with open(DATA_JSON, "r", encoding="utf-8") as f:
            d = json.load(f)
            docs.append({"id":"data_json", "content": json.dumps(d), "source": DATA_JSON})
    # provider files
    for p in [SHYAMOLI_PATH, SOUDIA_PATH]:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
                docs.append({"id": Path(p).stem, "content": content, "source": p})
    return docs

_docs_cache = None
def _get_docs():
    global _docs_cache
    if _docs_cache is None:
        _docs_cache = load_documents()
    return _docs_cache

def retrieve(query: str, k: int = 3):
    """
    Simple keyword matching retrieval: score docs by count of query tokens present.
    Returns top-k docs and matching snippets.
    """
    docs = _get_docs()
    qtokens = [t.lower() for t in query.split() if len(t) > 2]
    scored = []
    for d in docs:
        text = d["content"].lower()
        score = sum(text.count(t) for t in qtokens)
        if score > 0:
            # produce a short snippet where tokens appear
            first_pos = min((text.find(t) for t in qtokens if text.find(t) >= 0), default=0)
            snippet = text[first_pos:first_pos+300] if first_pos >=0 else text[:300]
            scored.append((score, {**d, "snippet": snippet[:500]}))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:k]]

def generate_answer(query: str, results: List[dict]):
    """
    Compose an answer using retrieved documents (very simple).
    """
    if not results:
        return "I couldn't find information in the local knowledge base for that question."
    lines = []
    lines.append(f"Answer based on {len(results)} retrieved document(s):")
    for r in results:
        lines.append(f"---\nSource: {r['source']}\nSnippet: {r['snippet'][:500]}\n")
    # Basic attempt to synthesize:
    lines.append("\nSynthesis: ")
    if "contact" in query.lower() or "contact details" in query.lower() or "phone" in query.lower():
        # find provider names in docs
        contacts = []
        for r in results:
            # naive extract phone-like tokens
            import re
            phones = re.findall(r"\b0\d{10}\b|\b\d{2,4}-\d{6,8}\b", r["content"])
            if phones:
                contacts.append({"source": r["source"], "phones": phones})
        if contacts:
            lines.append("Found contact numbers: " + "; ".join([f"{c['source']}: {', '.join(c['phones'])}" for c in contacts]))
        else:
            lines.append("No explicit phone numbers found in retrieved docs.")
    else:
        lines.append("See snippets above for relevant information.")
    return "\n".join(lines)
