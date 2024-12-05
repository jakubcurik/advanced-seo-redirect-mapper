from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


def weighted_embedding(content_dict: dict, weights: dict = None):
    if weights is None:
        # Nastavíme defaultní váhy. Tyto váhy můžeš podle potřeby měnit.
        # Například vyšší váha na title a headings, střední na slug a internal links, nižší na body text.
        weights = {
            "title": 3.0,
            "meta_desc": 2.0,
            "url_slug": 2.0,
            "headings": 2.5,
            "body_text": 1.0,
            "internal_links": 1.5
        }

    # Každý kus obsahu vynásobíme příslušnou vahou opakováním textu.
    # Případně by šlo text vynásobit nějak jinak, ale toto je jednoduché řešení.
    weighted_text = (
            ((content_dict.get("title", "") + " ") * int(weights["title"])) +
            ((content_dict.get("meta_desc", "") + " ") * int(weights["meta_desc"])) +
            ((content_dict.get("url_slug", "") + " ") * int(weights["url_slug"])) +
            ((content_dict.get("headings", "") + " ") * int(weights["headings"])) +
            ((content_dict.get("body_text", "") + " ") * int(weights["body_text"])) +
            ((content_dict.get("internal_links", "") + " ") * int(weights["internal_links"]))
    ).strip()

    return model.encode([weighted_text], show_progress_bar=False)[0]
