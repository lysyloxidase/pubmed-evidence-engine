from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from backend.core.search import search_combined
from backend.core.annotations import fetch_annotations_for_article
from backend.core.reranker import rerank_documents
from backend.core.generator import generate_report
from backend.core.graph import build_knowledge_graph

app = FastAPI(title="PubMed Evidence Engine API")

class QueryRequest(BaseModel):
    query: str
    limit: int = 20
    top_k: int = 5
    llm_model: str = "llama3"

class QueryResponse(BaseModel):
    query: str
    report: str
    documents: List[Dict[str, Any]]
    graph_data: Dict[str, Any]

@app.post("/api/query", response_model=QueryResponse)
async def process_query(req: QueryRequest):
    docs = search_combined(req.query, limit=req.limit)
    if not docs:
        raise HTTPException(status_code=404, detail="No documents found.")
        
    ranked_docs = rerank_documents(req.query, docs, top_k=req.top_k)
    
    annotations_map = {}
    for doc in ranked_docs:
        doc_id = doc.get("pmid", doc.get("id"))
        source = doc.get("source", "MED")
        if doc_id:
            anns = fetch_annotations_for_article(str(doc_id), source=source)
            annotations_map[str(doc_id)] = anns
            doc["annotations"] = anns 
            
    report = generate_report(req.query, ranked_docs, model_name=req.llm_model)
    graph_data = build_knowledge_graph(ranked_docs, annotations_map)
    
    return QueryResponse(
        query=req.query,
        report=report,
        documents=ranked_docs,
        graph_data=graph_data
    )

@app.get("/")
def health_check():
    return {"status": "ok"}
