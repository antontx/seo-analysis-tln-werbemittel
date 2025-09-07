#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json

def fetch_and_analyze(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    session = requests.Session()
    response = session.get(url, headers=headers, timeout=30)

    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Cookies: {session.cookies.get_dict()}")

    soup = BeautifulSoup(response.text, 'lxml')

    # Save the HTML
    with open('homepage.html', 'w', encoding='utf-8') as f:
        f.write(response.text)

    # Extract basic info
    title = soup.find('title')
    print(f"\nTitle: {title.text if title else 'Not found'}")

    # Meta tags
    metas = soup.find_all('meta')
    print(f"\nMeta tags found: {len(metas)}")
    for meta in metas[:10]:  # First 10 meta tags
        print(f"  {meta.attrs}")

    # Headers
    print(f"\nH1 tags: {len(soup.find_all('h1'))}")
    print(f"H2 tags: {len(soup.find_all('h2'))}")

    # Links
    print(f"\nTotal links: {len(soup.find_all('a'))}")
    print(f"Total images: {len(soup.find_all('img'))}")

    return response.text

if __name__ == "__main__":
    content = fetch_and_analyze("https://www.tln-werbemittel.de")
    print(f"\nTotal page size: {len(content)} bytes")
