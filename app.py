import streamlit as st
import pandas as pd
import asyncio
import nest_asyncio
from data_loader import extract_urls
from main import filter_and_unify_urls, scrape_and_process_async

nest_asyncio.apply()

st.title("Advanced SEO Redirect Mapper")
st.header("Nahrajte soubory s původními a novými URL")

if 'cleaned' not in st.session_state:
    st.session_state['cleaned'] = False
    st.session_state['cleaned_old_urls'] = []
    st.session_state['cleaned_new_urls'] = []

uploaded_old_file = st.file_uploader("Nahrajte soubor se starými URL (CSV, XLSX, TSV):", type=['csv', 'xlsx', 'tsv'])
uploaded_new_file = st.file_uploader("Nahrajte soubor s novými URL (CSV, XLSX, TSV):", type=['csv', 'xlsx', 'tsv'])

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
            cleaned_old_urls = filter_and_unify_urls(old_urls)
            cleaned_new_urls = filter_and_unify_urls(new_urls)
            st.success(f"Čištění dokončeno! Počet starých URL: {len(cleaned_old_urls)}, počet nových URL: {len(cleaned_new_urls)}")
            st.session_state['cleaned'] = True
            st.session_state['cleaned_old_urls'] = cleaned_old_urls
            st.session_state['cleaned_new_urls'] = cleaned_new_urls

        if st.session_state['cleaned']:
            if st.button("Spustit scraping URL"):
                with st.spinner("Probíhá scraping..."):
                    # Zde voláme async funkci, která vrací coroutine, a spustíme ji pomocí asyncio.run
                    scraped_old_data = asyncio.run(scrape_and_process_async(st.session_state['cleaned_old_urls'], exclude_selectors=[], weights=None))
                    scraped_new_data = asyncio.run(scrape_and_process_async(st.session_state['cleaned_new_urls'], exclude_selectors=[], weights=None))

                    st.subheader("Výsledky scrapingu pro staré URL")
                    scraped_old_df = pd.DataFrame(scraped_old_data)
                    st.write(scraped_old_df)

                    st.subheader("Výsledky scrapingu pro nové URL")
                    scraped_new_df = pd.DataFrame(scraped_new_data)
                    st.write(scraped_new_df)

    except Exception as e:
        st.error(f"Chyba při načítání nebo zpracování souborů: {e}")
