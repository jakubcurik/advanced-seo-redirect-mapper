import streamlit as st
import pandas as pd
import json
import plotly.express as px
import os
from clustering import reduce_embeddings

st.title("SEO Redirect Mapper")

st.subheader("Nastavení vah")
title_w = st.slider("Title weight", 0.0, 5.0, 2.5, 0.5)
meta_w = st.slider("Meta Desc weight", 0.0, 5.0, 0.5, 0.5)
slug_w = st.slider("URL Slug weight", 0.0, 5.0, 3.0, 0.5)
head_w = st.slider("Headings weight", 0.0, 5.0, 2.5, 0.5)
body_w = st.slider("Body weight", 0.0, 5.0, 2.0, 0.5)
links_w = st.slider("Internal Links weight", 0.0, 5.0, 1.5, 0.5)

if st.button("Přegenerovat embeddings a párování"):
    weights = {
        "title": title_w,
        "meta_desc": meta_w,
        "url_slug": slug_w,
        "headings": head_w,
        "body_text": body_w,
        "internal_links": links_w
    }
    with open('weights.json', 'w', encoding='utf-8') as f:
        json.dump(weights, f)
    st.write("Váhy uloženy do weights.json. Nyní spusť ručně `main.py` pro přegenerování.")

st.subheader("Filtr podle similarity score")
score_filter = st.slider("Min similarity", 0.0, 1.0, 0.8, 0.05)

if st.button("Zobrazit výsledky"):
    if not os.path.exists('redirect_map.csv'):
        st.write("redirect_map.csv neexistuje. Spusť main.py nejdříve.")
    else:
        df = pd.read_csv('redirect_map.csv')
        filtered_df = df[df["similarity_score"] >= score_filter]
        st.write(filtered_df)

if st.button("Zobrazit clustery"):
    if not (os.path.exists('new_data_embeddings.csv') and os.path.exists('labels.csv')):
        st.write("Soubory pro clustery neexistují. Spusť main.py nejdříve.")
    else:
        new_data_df = pd.read_csv('new_data_embeddings.csv')
        labels_df = pd.read_csv('labels.csv')
        urls = new_data_df['url'].tolist()
        embeddings = new_data_df.drop('url', axis=1).values
        labels = labels_df['label'].values

        X_reduced = reduce_embeddings(embeddings)

        df_vis = pd.DataFrame({
            'x': X_reduced[:,0],
            'y': X_reduced[:,1],
            'label': labels,
            'url': urls
        })

        fig = px.scatter(df_vis, x='x', y='y', color='label', hover_data=['url'])
        st.plotly_chart(fig)
