import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def scrape_url(url: str, exclude_selectors: list = None) -> dict:
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return get_empty_content(url)

        soup = BeautifulSoup(r.text, 'html.parser')

        # Vyloučení prvků podle CSS selektorů
        if exclude_selectors:
            for sel in exclude_selectors:
                for el in soup.select(sel):
                    el.decompose()

        # Odstraníme skripty a styly
        for s in soup(["script", "style"]):
            s.decompose()

        # Extrakce title
        title = soup.title.string.strip() if soup.title and soup.title.string else ''

        # Meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        meta_desc = desc_tag['content'].strip() if desc_tag and desc_tag.get('content') else ''

        # URL slug (poslední část z path)
        parsed_url = urlparse(url)
        path_parts = [p for p in parsed_url.path.split('/') if p]
        url_slug = path_parts[-1] if path_parts else ''

        # Nadpisy h1-h6
        # Můžeme je seřadit podle úrovně, tady je jen pospojíme do jednoho textu
        headings = []
        for level in range(1, 7):
            for h in soup.find_all(f'h{level}'):
                headings.append(h.get_text().strip())
        headings_text = ' '.join(headings)

        # Celkový text stránky
        body_text = ' '.join(s.strip() for s in soup.stripped_strings)

        # Interní odkazy: odkazy, které mají stejné doménové jméno
        domain = parsed_url.netloc
        internal_links_texts = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Zkusíme rozlišit interní odkaz
            parsed_link = urlparse(href)
            # Pokud není doména nebo stejná doména, považujeme za interní
            if (not parsed_link.netloc) or (parsed_link.netloc == domain):
                anchor_text = a.get_text().strip()
                if anchor_text:
                    internal_links_texts.append(anchor_text)
        internal_links_str = ' '.join(internal_links_texts)

        return {
            "title": title,
            "meta_desc": meta_desc,
            "url_slug": url_slug,
            "headings": headings_text,
            "body_text": body_text,
            "internal_links": internal_links_str
        }
    except:
        return get_empty_content(url)


def get_empty_content(url: str) -> dict:
    return {
        "title": "",
        "meta_desc": "",
        "url_slug": "",
        "headings": "",
        "body_text": "",
        "internal_links": ""
    }
