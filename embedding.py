from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def weighted_embedding(content_dict: dict, weights: dict = None):
    if weights is None:
        weights = {
            "title": 2.5,
            "meta_desc": 0.5,
            "url_slug": 3.0,
            "headings": 2.5,
            "body_text": 2.0,
            "internal_links": 1.5
        }

    # Načtení textu z content_dict
    title_text = content_dict.get("title", "")
    meta_text = content_dict.get("meta_desc", "")
    slug_text = content_dict.get("url_slug", "")
    head_text = content_dict.get("headings", "")
    body_text = content_dict.get("body_text", "")
    links_text = content_dict.get("internal_links", "")

    # Embedding pro každou část
    title_emb = model.encode([title_text], show_progress_bar=False)[0]
    meta_emb = model.encode([meta_text], show_progress_bar=False)[0]
    slug_emb = model.encode([slug_text], show_progress_bar=False)[0]
    head_emb = model.encode([head_text], show_progress_bar=False)[0]
    body_emb = model.encode([body_text], show_progress_bar=False)[0]
    links_emb = model.encode([links_text], show_progress_bar=False)[0]

    # Výpočet váženého průměru
    total_weight = (weights["title"] + weights["meta_desc"] + weights["url_slug"] +
                    weights["headings"] + weights["body_text"] + weights["internal_links"])

    weighted_sum = (title_emb * weights["title"] +
                    meta_emb * weights["meta_desc"] +
                    slug_emb * weights["url_slug"] +
                    head_emb * weights["headings"] +
                    body_emb * weights["body_text"] +
                    links_emb * weights["internal_links"])

    return weighted_sum / total_weight
