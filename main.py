from data_loader import load_urls
from scraper import scrape_url
from embedding import weighted_embedding
from clustering import cluster_urls, find_best_match
import pandas as pd
import requests
from urllib.parse import urlparse, urlunparse

exclude_selectors = ['header', 'footer', '.sidebar', '.header', '.footer', '.navigation', '.menu']

def unify_url(url: str) -> str:
    parsed = urlparse(url)
    # Odstranění trailing slash, pokud není root path
    path = parsed.path
    if path.endswith('/') and path != '/':
        path = path.rstrip('/')
    # Opětovné složení URL
    unified = urlunparse((parsed.scheme, parsed.netloc, path, '', '', ''))
    return unified

def filter_and_unify_urls(urls: list) -> list:
    # Unifikace trailing slash
    unified_urls = [unify_url(u) for u in urls]
    # Dedup
    unified_urls = list(set(unified_urls))

    valid_urls = []
    for u in unified_urls:
        try:
            # Povolení redirectů (ve výchozím stavu True)
            r = requests.get(u, timeout=10)
            # Pokud status != 200, zkusíme finální r.url unifikovat (po redirectu)
            if r.status_code == 200:
                final_u = unify_url(r.url)
                valid_urls.append(final_u)
            # Pokud ne 200, zahodíme
        except:
            # Pokud nastane chyba (timeout, DNS), URL ignorujeme
            pass

    # Znovu dedup po redirectech (mohlo se stát, že 2 různé URL vedou na stejnou finální stránku)
    valid_urls = list(set(valid_urls))
    return valid_urls

# Načteme staré a nové URL
old_urls = load_urls('old_data.csv')
new_urls = load_urls('new_data.csv')
print(f"Načteno {len(old_urls)} starých URL a {len(new_urls)} nových URL")

# Unifikace a filtrace starých URL
old_urls = filter_and_unify_urls(old_urls)
# Unifikace a filtrace nových URL
new_urls = filter_and_unify_urls(new_urls)

print(f"Po filtraci zbylo {len(old_urls)} starých a {len(new_urls)} nových URL.")

old_data = []
print("Zpracovávám staré URL...")
for i, url in enumerate(old_urls, 1):
    print(f"({i}/{len(old_urls)}) Stahuji: {url}")
    content_dict = scrape_url(url, exclude_selectors=exclude_selectors)
    emb = weighted_embedding(content_dict)
    old_data.append((url, emb))

new_data = []
print("\nZpracovávám nové URL...")
for i, url in enumerate(new_urls, 1):
    print(f"({i}/{len(new_urls)}) Stahuji: {url}")
    content_dict = scrape_url(url, exclude_selectors=exclude_selectors)
    emb = weighted_embedding(content_dict)
    new_data.append((url, emb))

new_embeddings = [emb for (_, emb) in new_data]
new_labels = cluster_urls(new_embeddings)

matches = []
print("\nPáruji staré URL s novými...")
for i, (old_url, old_emb) in enumerate(old_data, 1):
    print(f"({i}/{len(old_data)}) Páruji: {old_url}")
    idx, score = find_best_match(old_emb, [emb for (_, emb) in new_data], new_labels)
    best_new_url = new_data[idx][0]
    matches.append((old_url, best_new_url, score))

df = pd.DataFrame(matches, columns=['old_url', 'new_url', 'similarity_score'])
df.to_csv('redirect_map.csv', index=False)
print("Redirect mapa uložena do redirect_map.csv")
print("Hotovo.")

#HOTOVO