import streamlit as st
from transformers import AutoModel, AutoTokenizer
import torch

_model = None
_tokenizer = None
_current_model_name = None

def get_model_and_tokenizer():
    global _model, _tokenizer, _current_model_name

    # Získáme vybraný model z session_state, pokud není nastaven, použijeme defaultní
    if 'selected_model' in st.session_state:
        selected_model_name = st.session_state['selected_model']
    else:
        selected_model_name = "Seznam/retromae-small-cs"

    if _model is None or _tokenizer is None or _current_model_name != selected_model_name:
        _tokenizer = AutoTokenizer.from_pretrained(selected_model_name)
        _model = AutoModel.from_pretrained(selected_model_name)
        _model.eval()
        _current_model_name = selected_model_name

    return _model, _tokenizer

def get_embedding_from_text(text: str):
    model, tokenizer = get_model_and_tokenizer()
    inputs = tokenizer([text], max_length=512, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**inputs)
    cls_emb = outputs.last_hidden_state[:, 0, :]
    return cls_emb[0]

def weighted_embedding(content_dict: dict, weights: dict):
    model, tokenizer = get_model_and_tokenizer()
    title_text = content_dict.get("title", "")
    meta_text = content_dict.get("meta_desc", "")
    slug_text = content_dict.get("url_slug", "")
    head_text = content_dict.get("headings", "")
    body_text = content_dict.get("body_text", "")
    links_text = content_dict.get("internal_links", "")

    title_emb = get_embedding_from_text(title_text)
    meta_emb = get_embedding_from_text(meta_text)
    slug_emb = get_embedding_from_text(slug_text)
    head_emb = get_embedding_from_text(head_text)
    body_emb = get_embedding_from_text(body_text)
    links_emb = get_embedding_from_text(links_text)

    total_weight = (
        weights["title"] + weights["meta_desc"] + weights["url_slug"] +
        weights["headings"] + weights["body_text"] + weights["internal_links"]
    )

    weighted_sum = (
        title_emb * weights["title"] +
        meta_emb * weights["meta_desc"] +
        slug_emb * weights["url_slug"] +
        head_emb * weights["headings"] +
        body_emb * weights["body_text"] +
        links_emb * weights["internal_links"]
    )

    weighted_emb = (weighted_sum / total_weight).detach().cpu().numpy().astype("float32")
    return weighted_emb
