import asyncio
from urllib.parse import urlparse, urlunparse
import pandas as pd
import json
import os
import numpy as np
import aiohttp
from scraper import scrape_urls_async
from embedding import weighted_embedding
from clustering import cluster_urls, find_best_match
from clustering import reduce_embeddings
from cache_manager import get_from_cache, set_to_cache
from sklearn.metrics.pairwise import cosine_similarity
import hashlib

exclude_selectors = ['header', 'footer', '.sidebar', '.header', '.footer', '.navigation', '.menu']

def load_weights(file_path: str = 'weights.json') -> dict:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "title": 2.5,
        "meta_desc": 0.5,
        "url_slug": 3.0,
        "headings": 2.5,
        "body_text": 2.0,
        "internal_links": 1.5
    }

async def validate_urls_async(urls: list) -> list:
    valid_urls = []
    connector = aiohttp.TCPConnector(limit_per_host=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for u in urls:
            tasks.append(check_url(session, u))
        results = await asyncio.gather(*tasks)
    for url, ok in results:
        if ok:
            valid_urls.append(url)
    return valid_urls

async def check_url(session, url: str):
    try:
        async with session.get(url, timeout=5) as response:
            if response.status == 200:
                return url, True
    except:
        pass
    return url, False

def unify_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip('/') if parsed.path != '/' else parsed.path
    return urlunparse((parsed.scheme, parsed.netloc, path, '', '', ''))

async def filter_and_unify_urls_async(urls: list) -> list:
    unified_urls = list(set(unify_url(u) for u in urls))
    valid_urls = await validate_urls_async(unified_urls)
    return valid_urls

def compute_content_hash(content: dict) -> str:
    content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(content_str.encode('utf-8')).hexdigest()

async def async_process_urls(urls: list, exclude_selectors: list, weights: dict, transform_method: str, max_connections: int, delay_between_requests: float) -> list:
    fresh_data = await scrape_urls_async(urls, exclude_selectors, max_connections, delay_between_requests)

    result = []
    for u, c in zip(urls, fresh_data):
        new_hash = compute_content_hash(c)
        cached = get_from_cache(u)

        if cached is not None:
            old_hash = cached.get("hash")
            if old_hash == new_hash and "embedding" in cached:
                emb = np.array(cached["embedding"], dtype=np.float32)
                result.append({"url": u, "content": c, "embedding": emb})
                continue

        emb = weighted_embedding(c, weights).astype(np.float32)
        new_data = {
            "content": c,
            "embedding": emb.tolist(),
            "hash": new_hash
        }
        set_to_cache(u, new_data)
        result.append({"url": u, "content": c, "embedding": emb})

    if transform_method in ["PCA", "UMAP"]:
        all_emb = [x["embedding"] for x in result]
        # all_emb je list numpy arrayů float32
        reduced = reduce_embeddings(all_emb, method=transform_method).astype(np.float32)
        for i in range(len(result)):
            result[i]["embedding"] = reduced[i]
            u = result[i]["url"]
            cached = get_from_cache(u)
            if cached is not None:
                cached["embedding"] = reduced[i].tolist()
                set_to_cache(u, cached)

    return result

async def scrape_and_process_async(urls: list, exclude_selectors: list, weights: dict, transform_method: str, max_connections: int, delay_between_requests: float) -> list:
    return await async_process_urls(urls, exclude_selectors, weights, transform_method, max_connections, delay_between_requests)

def match_urls(old_data: list, new_data: list, new_labels: list, similarity_threshold: float = 0.5) -> pd.DataFrame:
    matches = []
    old_embeddings = [(x["url"], x["embedding"]) for x in old_data]
    new_embeddings = [(x["url"], x["embedding"]) for x in new_data]

    for i, (old_url, old_emb) in enumerate(old_embeddings, 1):
        idx, score = find_best_match(old_emb, [emb for (_, emb) in new_embeddings], new_labels)
        best_new_url = new_embeddings[idx][0]
        if score >= similarity_threshold:
            matches.append((old_url, best_new_url, score))
        else:
            matches.append((old_url, "no-match", score))

    return pd.DataFrame(matches, columns=['old_url', 'new_url', 'similarity_score'])

def save_results(matches: pd.DataFrame, new_data: list, new_labels: list):
    matches.to_csv('redirect_map.csv', index=False)
    urls_new = [x["url"] for x in new_data]
    emb_arr = np.array([x["embedding"] for x in new_data])
    emb_df = pd.DataFrame(emb_arr)
    emb_df.insert(0, 'url', urls_new)
    emb_df.to_csv('new_data_embeddings.csv', index=False)

    labels_df = pd.DataFrame({'label': new_labels})
    labels_df.to_csv('labels.csv', index=False)
