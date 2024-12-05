import pandas as pd


def load_urls(path: str) -> list:
    # Použijeme on_bad_lines='skip' místo error_bad_lines a warn_bad_lines
    df = pd.read_csv(path, sep=';', encoding='utf-8-sig', on_bad_lines='skip')

    columns_lower = [c.lower() for c in df.columns]
    url_col_candidates = [c for c in columns_lower if "url" in c]
    if not url_col_candidates:
        raise ValueError(f"V souboru {path} nebyl nalezen žádný sloupec obsahující 'url' v názvu.")

    url_col = df.columns[columns_lower.index(url_col_candidates[0])]
    return df[url_col].dropna().tolist()
