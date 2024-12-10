import pandas as pd
from io import BytesIO


def load_data(file) -> pd.DataFrame:

    #Načte soubor (CSV, TSV, nebo XLSX) a vrátí DataFrame.
    #Streamlit's UploadedFile object needs to be handled differently
    if file.name.endswith('.csv'):
        return pd.read_csv(file, sep=',', encoding='utf-8-sig', on_bad_lines='skip')
    elif file.name.endswith('.tsv'):
        return pd.read_csv(file, sep='\t', encoding='utf-8-sig', on_bad_lines='skip')
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file, engine='openpyxl')
    else:
        raise ValueError(f"Nepodporovaný formát souboru: {file.name}")


def find_url_column(df: pd.DataFrame) -> str:

    #Najde pravděpodobný sloupec obsahující URL adresy.
    columns_lower = [col.lower() for col in df.columns]
    url_col_candidates = [col for col in columns_lower if "url" in col]

    if not url_col_candidates:
        raise ValueError("Nebyl nalezen žádný sloupec obsahující 'url' v názvu.")

    return df.columns[columns_lower.index(url_col_candidates[0])]


def extract_urls(file) -> (pd.DataFrame, str):

    #Načte soubor a vrátí DataFrame a pravděpodobný název sloupce s URL.
    df = load_data(file)
    url_col = find_url_column(df)
    return df, url_col
