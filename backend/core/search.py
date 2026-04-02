import httpx
from typing import List, Dict, Any
from backend.core.cache import cache
import xml.etree.ElementTree as ET
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@cache.memoize(expire=86400)
def fetch_europe_pmc(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": query,
        "format": "json",
        "resultType": "core",
        "pageSize": limit
    }
    try:
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        return data.get("resultList", {}).get("result", [])
    except Exception as e:
        logger.error(f"Europe PMC search failed: {e}")
        return []

@cache.memoize(expire=86400)
def fetch_pubmed_entrez(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": limit
    }
    try:
        response = httpx.get(search_url, params=search_params, timeout=10.0)
        response.raise_for_status()
        pmids = response.json().get("esearchresult", {}).get("idlist", [])
        if not pmids:
            return []
        
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml"
        }
        resp = httpx.get(fetch_url, params=fetch_params, timeout=15.0)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
        
        results = []
        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID")
            title = article.findtext(".//ArticleTitle")
            abstract = ""
            for abstex in article.findall(".//AbstractText"):
                if abstex.text:
                    abstract += abstex.text + " "
            
            # Additional metadata could be extracted here
            results.append({
                "id": pmid,
                "source": "MED",
                "title": title,
                "abstractText": abstract.strip(),
                "pmid": pmid
            })
        return results
    except Exception as e:
        logger.error(f"PubMed Entrez search failed: {e}")
        return []

def search_combined(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    epmc_results = fetch_europe_pmc(query, limit=limit)
    sub_limit = max(5, limit // 2)
    pubmed_results = fetch_pubmed_entrez(query, limit=sub_limit)
    
    seen_ids = set()
    merged = []
    
    for doc in epmc_results:
        doc_id = doc.get("pmid") or doc.get("id")
        if doc_id:
            seen_ids.add(str(doc_id))
        merged.append(doc)
        
    for doc in pubmed_results:
        doc_id = doc.get("pmid")
        if doc_id and str(doc_id) not in seen_ids:
            seen_ids.add(str(doc_id))
            merged.append(doc)
            
    return merged[:limit]
