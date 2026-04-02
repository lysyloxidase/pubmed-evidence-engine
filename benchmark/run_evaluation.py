import httpx
import time
import json
import os

API_URL = "http://localhost:8000/api/query"
OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3"

EVAL_QUESTIONS = [
    "What are the molecular mechanisms of imatinib resistance in Chronic Myeloid Leukemia?",
    "How does APOE4 allele contribute to Alzheimer's disease pathogenesis?",
]

def run_baseline(query: str, model_name: str) -> str:
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": query}],
        "stream": False
    }
    try:
        r = httpx.post(OLLAMA_URL, json=payload, timeout=60.0)
        return r.json().get("message", {}).get("content", "")
    except:
        return "Failed"

def run_kag(query: str, model_name: str) -> dict:
    payload = {
        "query": query,
        "limit": 20,
        "top_k": 5,
        "llm_model": model_name
    }
    try:
        start = time.time()
        r = httpx.post(API_URL, json=payload, timeout=120.0)
        dur = time.time() - start
        if r.status_code == 200:
            data = r.json()
            return {"report": data["report"], "dur": dur, "num_docs": len(data["documents"])}
        return {"report": "API Error", "dur": dur, "num_docs": 0}
    except:
        return {"report": "Timeout", "dur": 0, "num_docs": 0}

def evaluate():
    results = []
    print("Running Evaluation Benchmark...")
    for q in EVAL_QUESTIONS:
        print(f"\nQ: {q}")
        print("Running Baseline...")
        base = run_baseline(q, DEFAULT_MODEL)
        print("Running PubMed Evidence Engine...")
        rag = run_kag(q, DEFAULT_MODEL)
        
        results.append({
            "question": q,
            "baseline": base,
            "system_rag": rag["report"],
            "duration": rag["dur"],
            "docs_used": rag["num_docs"]
        })
        
    report_path = os.path.join(os.path.dirname(__file__), "eval_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nEvaluation saved to {report_path}")

if __name__ == "__main__":
    evaluate()
