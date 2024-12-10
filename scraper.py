import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def clean_text(text: str) -> str:
    # Čistí text od bílých znaků a převádí na malá písmena
    text = text.lower()
    text = ' '.join(text.split())
    return text

def get_empty_content():
    # Vrací prázdný obsah
    return {
        "title": "",
        "meta_desc": "",
        "url_slug": "",
        "headings": "",
        "body_text": "",
        "internal_links": ""
    }

async def fetch(session, url: str):
    # Asynchronní načtení obsahu URL
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                print(f"Chyba: {url} - Stavový kód {response.status}")
                return None
            return await response.text()
    except Exception as e:
        print(f"Chyba při načítání URL {url}: {e}")
        return None

async def scrape_single_url(session, url: str, exclude_selectors: list = None) -> dict:
    # Scrapuje jednu URL a vrací strukturovaný obsah
    html = await fetch(session, url)
    if not html:
        return get_empty_content()

    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Odstranění vybraných selektorů
        if exclude_selectors:
            for sel in exclude_selectors:
                for el in soup.select(sel):
                    el.decompose()

        # Odstranění JavaScript a CSS
        for s in soup(["script", "style"]):
            s.decompose()

        # Titulek stránky
        title = soup.title.string.strip() if soup.title and soup.title.string else ''
        # Meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        meta_desc = desc_tag['content'].strip() if desc_tag and desc_tag.get('content') else ''

        # Slug z URL
        parsed_url = urlparse(url)
        path_parts = [p for p in parsed_url.path.split('/') if p]
        url_slug = path_parts[-1] if path_parts else ''

        # Nadpisy h1-h6
        headings = []
        for level in range(1, 7):
            for h in soup.find_all(f'h{level}'):
                headings.append(h.get_text().strip())
        headings_text = ' '.join(headings)

        # Celý text stránky
        body_text = ' '.join(s.strip() for s in soup.stripped_strings)

        # Interní odkazy
        domain = parsed_url.netloc
        internal_links_texts = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            anchor_text = a.get_text().strip()
            if anchor_text:
                parsed_link = urlparse(href)
                if (not parsed_link.netloc) or (parsed_link.netloc == domain):
                    internal_links_texts.append(anchor_text)
        internal_links_str = ' '.join(internal_links_texts)

        return {
            "title": clean_text(title),
            "meta_desc": clean_text(meta_desc),
            "url_slug": clean_text(url_slug),
            "headings": clean_text(headings_text),
            "body_text": clean_text(body_text),
            "internal_links": clean_text(internal_links_str)
        }
    except Exception as e:
        print(f"Chyba při scrapování URL {url}: {e}")
        return get_empty_content()

async def scrape_urls_async(urls: list, exclude_selectors: list = None, max_connections: int = 10) -> list:
    # Scrapuje více URL asynchronně
    results = []
    connector = aiohttp.TCPConnector(limit_per_host=max_connections)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [scrape_single_url(session, url, exclude_selectors) for url in urls]
        for task in asyncio.as_completed(tasks):
            result = await task
            results.append(result)
    return results
