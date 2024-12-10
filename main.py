import requests
import asyncio
from urllib.parse import urlparse, urlunparse
import pandas as pd
import json
import os
import numpy as np
from scraper import scrape_urls_async
from embedding import weighted_embedding
from clustering import cluster_urls, find_best_match

exclude_selectors = ['header', 'footer', '.sidebar', '.header', '.footer', '.navigation', '.menu']

def unify_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip('/') if parsed.path != '/' else parsed.path
    return urlunparse((parsed.scheme, parsed.netloc, path, '', '', ''))

def filter_and_unify_urls(urls: list) -> list:
    print("Normalizuji a deduplikuji URL...")
    unified_urls = list(set(unify_url(u) for u in urls))

    valid_urls = []
    for i, url in enumerate(unified_urls, 1):
        try:
            print(f"({i}/{len(unified_urls)}) Kontroluji: {url}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                final_url = unify_url(response.url)
                valid_urls.append(final_url)
        except requests.RequestException as e:
            print(f"Chyba u URL {url}: {e}")

    return list(set(valid_urls))

def load_weights(file_path: str = 'weights.json') -> dict:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

async def async_process_urls(urls: list, exclude_selectors: list, weights: dict) -> list:
    print("Spouštím asynchronní scraping...")
    scraped_data = await scrape_urls_async(urls, exclude_selectors)
    print("Scraping dokončen.")

    data = []
    for url, content in zip(urls, scraped_data):
        print(f"Generuji embeddingy pro URL: {url}")
        emb = weighted_embedding(content, weights)
        data.append({"url": url, "content": content, "embedding": emb})
    return data

async def scrape_and_process_async(urls: list, exclude_selectors: list, weights: dict) -> list:
    # Tato funkce je čistě async a vrací awaitable.
    return await async_process_urls(urls, exclude_selectors, weights)

def match_urls(old_data: list, new_data: list, new_labels: list, similarity_threshold: float = 0.5) -> pd.DataFrame:
    matches = []
    # old_data a new_data nyní obsahují dict s klíčem "url" a "embedding"
    # pro match musíme vytvořit list s old_emb a new_emb
    old_embeddings = [(x["url"], x["embedding"]) for x in old_data]
    new_embeddings = [(x["url"], x["embedding"]) for x in new_data]

    for i, (old_url, old_emb) in enumerate(old_embeddings, 1):
        print(f"({i}/{len(old_embeddings)}) Páruji: {old_url}")
        idx, score = find_best_match(old_emb, [emb for (_, emb) in new_embeddings], new_labels)
        best_new_url = new_embeddings[idx][0]
        if score >= similarity_threshold:
            matches.append((old_url, best_new_url, score))
        else:
            matches.append((old_url, "no-match", score))

    return pd.DataFrame(matches, columns=['old_url', 'new_url', 'similarity_score'])

def save_results(matches: pd.DataFrame, new_data: list, new_labels: list):
    print("\nUkládám výsledky...")
    matches.to_csv('redirect_map.csv', index=False)
    print("Redirect mapa uložena do redirect_map.csv")

    urls_new = [x["url"] for x in new_data]
    emb_arr = np.array([x["embedding"] for x in new_data])
    emb_df = pd.DataFrame(emb_arr)
    emb_df.insert(0, 'url', urls_new)
    emb_df.to_csv('new_data_embeddings.csv', index=False)

    labels_df = pd.DataFrame({'label': new_labels})
    labels_df.to_csv('labels.csv', index=False)

    print("new_data_embeddings.csv a labels.csv uloženy.")

def process_redirects(old_urls: list, new_urls: list, similarity_threshold: float = 0.5):
    print("Normalizuji a deduplikuji URL...")
    old_urls = filter_and_unify_urls(old_urls)
    new_urls = filter_and_unify_urls(new_urls)

    print(f"Po filtraci zbylo {len(old_urls)} starých a {len(new_urls)} nových URL.")

    weights = load_weights()

    # Tuto funkci byste použili, kdybyste chtěli spustit celou logiku bez Streamlitu
    # Např.:
    # old_data = asyncio.run(async_process_urls(old_urls, exclude_selectors, weights))
    # new_data = asyncio.run(async_process_urls(new_urls, exclude_selectors, weights))

    # Provádíme klastrování
    # new_embeddings = [x["embedding"] for x in new_data]
    # new_labels = cluster_urls(new_embeddings)
    # matches = match_urls(old_data, new_data, new_labels, similarity_threshold)
    # save_results(matches, new_data, new_labels)
    pass  # Tady je prázdné, protože teď spouštíme logiku z app.py
