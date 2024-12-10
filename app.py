import streamlit as st
import pandas as pd
import asyncio
import nest_asyncio
from data_loader import extract_urls
from main import filter_and_unify_urls_async, scrape_and_process_async, load_weights, cluster_urls, match_urls, save_results
import numpy as np
import os

nest_asyncio.apply()

st.title("Advanced SEO Redirect Mapper")

# Sidebar pro konfiguraci
st.sidebar.header("Konfigurace")
st.sidebar.subheader("Obecné")
similarity_threshold = st.sidebar.slider("Similarity threshold", 0.0, 1.0, 0.5, 0.05)

default_weights = load_weights()
w_title = st.sidebar.number_input("Váha TITLE", value=float(default_weights["title"]), step=0.1)
w_meta = st.sidebar.number_input("Váha META DESC", value=float(default_weights["meta_desc"]), step=0.1)
w_slug = st.sidebar.number_input("Váha URL SLUG", value=float(default_weights["url_slug"]), step=0.1)
w_headings = st.sidebar.number_input("Váha HEADINGS", value=float(default_weights["headings"]), step=0.1)
w_body = st.sidebar.number_input("Váha BODY TEXT", value=float(default_weights["body_text"]), step=0.1)
w_links = st.sidebar.number_input("Váha INTERNAL LINKS", value=float(default_weights["internal_links"]), step=0.1)

weights = {
    "title": w_title,
    "meta_desc": w_meta,
    "url_slug": w_slug,
    "headings": w_headings,
    "body_text": w_body,
    "internal_links": w_links
}

st.sidebar.subheader("Scraper nastavení")
max_connections = st.sidebar.number_input("Maximální paralelní připojení", min_value=1, max_value=100, value=10, step=1)
delay_between_requests = st.sidebar.number_input("Prodleva mezi requesty (s)", min_value=0.0, max_value=10.0, value=0.5, step=0.1)

st.header("Nahrajte soubory s původními a novými URL")

if 'cleaned' not in st.session_state:
    st.session_state['cleaned'] = False
    st.session_state['cleaned_old_urls'] = []
    st.session_state['cleaned_new_urls'] = []
    st.session_state['scraped_old_data'] = None
    st.session_state['scraped_new_data'] = None
    st.session_state['new_labels'] = None
    st.session_state['matches'] = None

uploaded_old_file = st.file_uploader("Nahrajte soubor se starými URL (CSV, XLSX, TSV):", type=['csv', 'xlsx', 'tsv'])
uploaded_new_file = st.file_uploader("Nahrajte soubor s novými URL (CSV, XLSX, TSV):", type=['csv', 'xlsx', 'tsv'])

transform_method = st.selectbox("Způsob zpracování embeddingů:", ["Lineární kombinace", "PCA", "UMAP"])

exclude_selectors_input = st.text_input("CSS selektory k vyloučení (oddělit čárkou)", value="header,footer,.sidebar,.header,.footer,.navigation,.menu")
exclude_selectors = [x.strip() for x in exclude_selectors_input.split(',') if x.strip()]

if uploaded_old_file and uploaded_new_file:
    try:
        st.subheader("Přehled sloupců ze souboru se starými URL")
        old_df, old_url_col = extract_urls(uploaded_old_file)
        old_df = old_df.fillna("N/A").astype(str)

        old_preview = pd.DataFrame(
            [old_df.columns, old_df.iloc[0]],
            index=["Sloupec", "Příklad"]
        )
        st.write(old_preview)

        selected_old_col = st.selectbox("Nalezený sloupec se starými URL:", old_df.columns, index=old_df.columns.get_loc(old_url_col))
        old_urls = old_df[selected_old_col].dropna().tolist()

        st.subheader("Přehled sloupců ze souboru s novými URL")
        new_df, new_url_col = extract_urls(uploaded_new_file)
        new_df = new_df.fillna("N/A").astype(str)

        new_preview = pd.DataFrame(
            [new_df.columns, new_df.iloc[0]],
            index=["Sloupec", "Příklad"]
        )
        st.write(new_preview)

        selected_new_col = st.selectbox("Nalezený sloupec s novými URL:", new_df.columns, index=new_df.columns.get_loc(new_url_col))
        new_urls = new_df[selected_new_col].dropna().tolist()

        if st.button("Spustit čištění URL"):
            with st.spinner("Probíhá čištění a validace..."):
                cleaned_old_urls = asyncio.run(filter_and_unify_urls_async(old_urls))
                cleaned_new_urls = asyncio.run(filter_and_unify_urls_async(new_urls))
            st.success(f"Čištění dokončeno! Počet starých URL: {len(cleaned_old_urls)}, počet nových URL: {len(cleaned_new_urls)}")
            st.session_state['cleaned'] = True
            st.session_state['cleaned_old_urls'] = cleaned_old_urls
            st.session_state['cleaned_new_urls'] = cleaned_new_urls

        if st.session_state['cleaned']:
            if st.button("Spustit scraping a embedding"):
                with st.spinner("Probíhá scraping a generování embeddingů..."):
                    chosen_transform = None
                    if transform_method == "PCA":
                        chosen_transform = "PCA"
                    elif transform_method == "UMAP":
                        chosen_transform = "UMAP"

                    # Předáme max_connections a delay_between_requests do scrape_and_process_async přes session_state
                    # Abychom to nemuseli měnit v main, předáme to do session a main.py upravíme:
                    # Budeme muset main.py upravit aby tyto parametry také převzal.

                    # Ale protože main.py nemá v kódu nic co by to brzdilo, upravíme main.py, aby:
                    # async_process_urls přijímal max_connections a delay_between_requests a předal je do scrape_urls_async

                    # To uděláme až na konci. Zatím předpokládejme, že main.py umí tyto parametry přijmout.
                    scraped_old_data = asyncio.run(scrape_and_process_async(
                        st.session_state['cleaned_old_urls'],
                        exclude_selectors,
                        weights,
                        chosen_transform,
                        max_connections,
                        delay_between_requests
                    ))

                    scraped_new_data = asyncio.run(scrape_and_process_async(
                        st.session_state['cleaned_new_urls'],
                        exclude_selectors,
                        weights,
                        chosen_transform,
                        max_connections,
                        delay_between_requests
                    ))

                    st.session_state['scraped_old_data'] = scraped_old_data
                    st.session_state['scraped_new_data'] = scraped_new_data

                    st.subheader("Výsledky scrapingu pro staré URL")
                    scraped_old_df = pd.DataFrame(scraped_old_data)
                    st.write(scraped_old_df)

                    st.subheader("Výsledky scrapingu pro nové URL")
                    scraped_new_df = pd.DataFrame(scraped_new_data)
                    st.write(scraped_new_df)

                    # Klastrování
                    new_embeddings = np.array([x["embedding"] for x in scraped_new_data])
                    new_labels = cluster_urls(new_embeddings)
                    st.session_state['new_labels'] = new_labels
                    st.success("Klastrování dokončeno.")

        # Pokud už máme data a klastrováno, nabídneme párování
        if st.session_state['scraped_old_data'] is not None and st.session_state['scraped_new_data'] is not None and st.session_state['new_labels'] is not None:
            if st.button("Spustit párování"):
                matches = match_urls(st.session_state['scraped_old_data'], st.session_state['scraped_new_data'], st.session_state['new_labels'], similarity_threshold)
                save_results(matches, st.session_state['scraped_new_data'], st.session_state['new_labels'])
                st.session_state['matches'] = matches
                st.success("Párování dokončeno. Soubor redirect_map.csv byl vygenerován.")

            if st.session_state['matches'] is not None:
                st.subheader("Redirect mapa")
                st.write(st.session_state['matches'])

                if os.path.exists('redirect_map.csv'):
                    with open('redirect_map.csv', 'rb') as f:
                        st.download_button(
                            label="Stáhnout redirect_map.csv",
                            data=f,
                            file_name="redirect_map.csv",
                            mime="text/csv"
                        )

    except Exception as e:
        st.error(f"Chyba při načítání nebo zpracování souborů: {e}")
