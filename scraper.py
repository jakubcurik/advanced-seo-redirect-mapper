import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def clean_text(text: str) -> str:
    text = text.lower()
    text = ' '.join(text.split())
    return text

def get_empty_content():
    return {
        "title": "",
        "meta_desc": "",
        "url_slug": "",
        "headings": "",
        "body_text": "",
        "internal_links": ""
    }

async def fetch(session, url: str, delay_between_requests: float):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                return None
            text = await response.text()
            if delay_between_requests > 0:
                await asyncio.sleep(delay_between_requests)
            return text
    except:
        return None

async def scrape_single_url(session, url: str, exclude_selectors: list = None, delay_between_requests: float = 0) -> dict:
    html = await fetch(session, url, delay_between_requests)
    if not html:
        return get_empty_content()

    try:
        soup = BeautifulSoup(html, 'html.parser')

        if exclude_selectors:
            for sel in exclude_selectors:
                for el in soup.select(sel):
                    el.decompose()

        for s in soup(["script", "style"]):
            s.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else ''
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        meta_desc = desc_tag['content'].strip() if desc_tag and desc_tag.get('content') else ''

        parsed_url = urlparse(url)
        path_parts = [p for p in parsed_url.path.split('/') if p]
        url_slug = path_parts[-1] if path_parts else ''

        headings = []
        for level in range(1, 7):
            for h in soup.find_all(f'h{level}'):
                headings.append(h.get_text().strip())
        headings_text = ' '.join(headings)

        body_text = ' '.join(s.strip() for s in soup.stripped_strings)

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
    except:
        return get_empty_content()

async def scrape_urls_async(urls: list, exclude_selectors: list = None, max_connections: int = 10, delay_between_requests: float = 0) -> list:
    connector = aiohttp.TCPConnector(limit_per_host=max_connections)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [scrape_single_url(session, url, exclude_selectors, delay_between_requests) for url in urls]
        results = await asyncio.gather(*tasks)
    return results

