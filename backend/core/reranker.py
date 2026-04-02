from sentence_transformers import CrossEncoder
from typing import List, Dict, Any

_encoder = None

def get_encoder():
    global _encoder
    if _encoder is None:
        # Using a small, efficient model for local execution
        _encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
    return _encoder

def rerank_documents(query: str, documents: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
    if not documents:
        return []
    
    encoder = get_encoder()
    pairs = []
    for doc in documents:
        abstract = doc.get('abstractText', '')
        title = doc.get('title', '')
        text = f"{title}. {abstract}"
        pairs.append((query, text))
        
    scores = encoder.predict(pairs)
    
    for i, doc in enumerate(documents):
        doc['rerank_score'] = float(scores[i])
        
    documents.sort(key=lambda x: x['rerank_score'], reverse=True)
    return documents[:top_k]
