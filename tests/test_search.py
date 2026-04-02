from backend.core.search import search_combined
from backend.core.annotations import fetch_annotations_for_article
import pytest

def test_search_combined():
    docs = search_combined("imatinib resistance", limit=5)
    assert len(docs) > 0
    assert "title" in docs[0]
    
def test_annotations_fetch():
    docs = search_combined("cancer", limit=1)
    if docs:
        pmid = docs[0].get("pmid")
        source = docs[0].get("source", "MED")
        if pmid:
            anns = fetch_annotations_for_article(str(pmid), source=source)
            assert isinstance(anns, list)
