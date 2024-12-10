import json
import os

CACHE_FILE = 'cache.json'

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache_data):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False)

def get_from_cache(url: str):
    cache_data = load_cache()
    return cache_data.get(url, None)

def set_to_cache(url: str, data: dict):
    cache_data = load_cache()
    cache_data[url] = data
    save_cache(cache_data)
