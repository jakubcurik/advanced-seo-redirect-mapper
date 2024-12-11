
# Advanced SEO Redirect Mapper

Advanced SEO Redirect Mapper je nástroj pro tvorbu map přesměrování při změnách URL adres. Je navržen tak, aby během redesignu, migrace či restrukturalizace webu pomohl přiřadit staré URL k novým stránkám.

## Klíčové funkce

- **Nahrání starých a nových URL**: Uživatel načte dva soubory (CSV, TSV, XLSX) se seznamem původních a nových URL.
- **Čištění, validace a unifikace URL**: Nástroj automaticky odstraní duplicity, trailing slashe, ověří funkčnost URL a sjednotí jejich formát.
- **Asynchronní scraping obsahu**: Pro každou URL se asynchronně stáhne obsah (title, meta desc, headings, body text, interní odkazy) a extrahuje klíčové informace.
- **Odstranění zvolených selektorů**: Konfigurovatelné CSS selektory umožňují ignorovat např. hlavičku, patičku, menu, aby embeddingy lépe reprezentovaly hlavní obsah.
- **Generování embeddingů**: Pomocí RetroMAE-Small-cs (pro české texty) nebo jiného modelu se vygenerují embeddingy. Váhy jednotlivých částí obsahu lze nastavit.
- **Klastrování a párování**: Nové URL se klastrují pro odhalení tematických celků. Staré URL se pak přiřadí k nejpodobnějším novým URL na základě kosinové podobnosti embeddingů.
- **Asynchronní validace a caching**: URL jsou validovány asynchronně pro rychlejší kontrolu. Výsledky scrapingu a embeddingů se cachují, aby opakované běhy byly efektivnější.
- **Konfigurace scraperu a dávkování requestů**: Lze nastavit počet paralelních připojení a pauzy mezi requesty či dávkami pro minimalizaci rizika blokací ze strany serverů.
- **Výstup redirect mapy**: Generuje se `redirect_map.csv`, který přiřazuje staré URL k novým cílovým URL.

## Spuštění webové aplikace
Spuštění hostované aplikace je ta nejrychlejší a nejjednoduší možnost, jak nsátroj spustit a začít používat.

Stačí přejít na tuto adresu: https://advanced-redirect-mapper.streamlit.app/

## Instalace ve vlastním prostředí
Projekt vyžaduje Python 3.12. Doporučuju použít virtuální prostředí.
1. **Klonování repozitáře**:

    ```bash
    git clone https://github.com/uzivatel/advanced-seo-redirect-mapper
    cd advanced-seo-redirect-mapper
    ```

2. **Vytvoření a aktivace virtuálního prostředí (doporučeno)**:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Na Windows: .venv\Scripts\activate
    ```

3. **Instalace závislostí**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Spuštění lokálně**:

    ```bash
    streamlit run app.py
    ```

## Použití nástroje v praxi

1. Nahrajte soubor se starými URL a novými URL.
2. V interface nastavte správné sloupce obsahující URL.
3. Spusťte čištění a validaci URL.
4. Po vyčištění klikněte na „Spustit scraping a embedding“. Nástroj:
    - Stáhne obsah všech URL.
    - Vygeneruje embeddingy (podle nastavení vah a transformace).
    - Provede klastrování nových URL.
5. Po dokončení máte možnost spustit „Párování“, které vytvoří `redirect_map.csv`.
6. `redirect_map.csv` si poté můžete stáhnout přímo z UI.

## Konfigurace přes UI

- **Similarity threshold**: Nastavuje minimální podobnost pro přiřazení starých URL k novým.
- **Váhy obsahu**: Upravte váhy `title`, `meta desc`, `slug`, `headings`, `body text` a `internal_links`, aby embeddingy lépe odpovídaly vašim potřebám.
- **Scraper Settings (Sidebar)**:
  - `max_connections`: Počet souběžných requestů.
  - `delay_between_requests`: Pauza mezi jednotlivými requesty v rámci dávky.
  - `batch_size` a `pause_after_batch` (v kódu): Velikost dávek a pauza mezi dávkami requestů.

## Časté problémy a jejich řešení

- **Různé dimenze embeddingů**: Ujistěte se, že používáte jednotný model a transformaci. Vymažte cache, pokud jste model změnili.
- **Chyba s multiprocessingem na Windows**: Načítejte model až po `if __name__ == '__main__':` nebo uvnitř funkce, aby se neprováděl při importu.
- **Nesoulad obsahu s URL**: Použijte `asyncio.gather()` namísto `asyncio.as_completed()`, aby byly výsledky scrapingu ve stejném pořadí jako seznam URL.

## Licenční informace

Tento nástroj využívá model `Seznam/retromae-small-cs` licencovaný pod CC-BY-4.0.
Ostatní závislosti jsou pod vlastními licencemi. Viz `requirements.txt`.
