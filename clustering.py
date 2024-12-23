import numpy as np
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import umap.umap_ as UMAP

def cluster_urls(embeddings: list):
    X = np.array(embeddings)
    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, metric='euclidean')
    labels = clusterer.fit_predict(X)
    return labels

def find_best_match(old_embedding, new_embeddings, new_labels):
    similarities = cosine_similarity([old_embedding], new_embeddings)[0]
    best_idx = similarities.argmax()
    return best_idx, similarities[best_idx]

def reduce_embeddings(embeddings, method="PCA"):
    X = np.array(embeddings)
    if X.shape[0] < 2:
        return X
    if method == "PCA":
        pca = PCA(n_components=2)
        X_reduced = pca.fit_transform(X)
        return X_reduced
    elif method == "UMAP":
        reducer = UMAP(n_components=2, random_state=42)
        X_reduced = reducer.fit_transform(X)
        return X_reduced
    else:
        return X
