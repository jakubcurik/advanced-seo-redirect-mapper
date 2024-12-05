from data_loader import load_urls
from scraper import scrape_url
from embedding import weighted_embedding
from clustering import cluster_urls, find_best_match
import pandas as pd

old_urls = load_urls('old_data.csv')
new_urls = load_urls('new_data.csv')

print(f"Načteno {len(old_urls)} starých URL a {len(new_urls)} nových URL")

exclude_selectors = ['header', 'footer', '.sidebar']  # příklad

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
