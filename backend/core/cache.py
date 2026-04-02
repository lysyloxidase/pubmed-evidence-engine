import diskcache as dc
import os

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", ".cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR, exist_ok=True)
cache = dc.Cache(CACHE_DIR)
