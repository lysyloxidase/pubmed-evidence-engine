import httpx
from typing import List, Dict, Any
from backend.core.cache import cache

@cache.memoize(expire=86400)
def fetch_annotations_for_article(article_id: str, source: str = "MED") -> List[Dict[str, Any]]:
    """
    Fetch annotations for a specific article from Europe PMC.
    source: typically 'MED' for PubMed, 'PMC' for PMC articles.
    """
    url = "https://www.ebi.ac.uk/europepmc/annotations_api/annotationsByArticleIds"
    params = {
        "articleIds": f"{source}:{article_id}",
        "format": "JSON"
    }
    try:
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        annotations = []
        for ann_list in data:
            for ann in ann_list.get("annotations", []):
                annotations.append({
                    "exact": ann.get("exact"),
                    "type": ann.get("type"), # e.g. 'Gene_Proteins', 'Diseases', 'Chemicals'
                    "tags": ann.get("tags", []),
                    "section": ann.get("section")
                })
        # Deduplicate
        seen = set()
        unique_annotations = []
        for a in annotations:
            key = (a["exact"], a["type"])
            if key not in seen and a["exact"]:
                seen.add(key)
                unique_annotations.append(a)
        return unique_annotations
    except Exception as e:
        print(f"Error fetching annotations for {source}:{article_id}: {e}")
        return []
