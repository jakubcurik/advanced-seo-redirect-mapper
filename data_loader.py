import csv
import pandas as pd

def load_data(file) -> pd.DataFrame:
    # Nejprve přečteme pár řádků z souboru, abychom mohli zdetekovat oddělovač.
    raw = file.read()
    file.seek(0)  # Vrátíme ukazatel na začátek souboru
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(raw.decode('utf-8', errors='replace').splitlines()[0])
    delimiter = dialect.delimiter
    file.seek(0)

    if file.name.endswith('.csv') or file.name.endswith('.tsv'):
        return pd.read_csv(file, sep=delimiter, encoding='utf-8-sig', on_bad_lines='skip')
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file, engine='openpyxl')
    else:
        raise ValueError(f"Nepodporovaný formát souboru: {file.name}")

def find_url_column(df: pd.DataFrame) -> str:
    columns_lower = [col.lower() for col in df.columns]
    url_col_candidates = [col for col in columns_lower if "url" in col]

    if not url_col_candidates:
        raise ValueError("Nebyl nalezen žádný sloupec obsahující 'url' v názvu.")

    return df.columns[columns_lower.index(url_col_candidates[0])]

def extract_urls(file) -> (pd.DataFrame, str):
    df = load_data(file)
    url_col = find_url_column(df)
    return df, url_col
