import httpx
from typing import List, Dict, Any

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3" # Users can override this, assuming llama3 exists.

def generate_report(query: str, documents: List[Dict[str, Any]], model_name: str = DEFAULT_MODEL) -> str:
    context_text = ""
    for i, doc in enumerate(documents):
        title = doc.get("title", "")
        abstract = doc.get("abstractText", "")
        source = f"{doc.get('source', '')}:{doc.get('pmid', doc.get('id', ''))}"
        context_text += f"[{i+1}] {title} ({source}): {abstract}\n\n"
        
    prompt = f"""You are a biomedical AI assistant. Given the following scientific abstracts, answer the user's question.
You MUST cite your sources using bracket notation corresponding to the document number (e.g., [1], [2]).
Do not hallucinate.

Question: {query}

Context:
{context_text}

Answer:"""

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a helpful biomedical assistant. Always read the provided context and use citations."},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    try:
        response = httpx.post(OLLAMA_URL, json=payload, timeout=90.0)
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "Error generating response.")
    except Exception as e:
        return f"Error connecting to local LLM: {e}. Are you sure Ollama is running and model '{model_name}' is downloaded?"
