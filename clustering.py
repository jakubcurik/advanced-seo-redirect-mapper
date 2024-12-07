import numpy as np
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity

def cluster_urls(embeddings: list):
    X = np.array(embeddings)
    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, metric='euclidean')
    labels = clusterer.fit_predict(X)
    return labels

def find_best_match(old_embedding, new_embeddings, new_labels):
    # Jednoduché nalezení nejlepší shody přes cosine similarity
    similarities = cosine_similarity([old_embedding], new_embeddings)[0]
    best_idx = similarities.argmax()
    return best_idx, similarities[best_idx]
