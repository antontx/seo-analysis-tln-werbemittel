#!/usr/bin/env python3
import re
from bs4 import BeautifulSoup
import json

# Read the HTML file
with open('homepage_raw.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'lxml')

analysis = {}

# Title
title = soup.find('title')
analysis['title'] = title.text.strip() if title else None
analysis['title_length'] = len(analysis['title']) if analysis['title'] else 0

# Meta tags
meta_tags = {}
for meta in soup.find_all('meta'):
    if meta.get('name'):
        meta_tags[meta['name']] = meta.get('content', '')
    elif meta.get('property'):
        meta_tags[meta['property']] = meta.get('content', '')
    elif meta.get('http-equiv'):
        meta_tags[meta['http-equiv']] = meta.get('content', '')

analysis['meta_tags'] = meta_tags

# Headings
analysis['h1'] = [h.text.strip() for h in soup.find_all('h1')]
analysis['h2'] = [h.text.strip() for h in soup.find_all('h2')]
analysis['h3'] = [h.text.strip() for h in soup.find_all('h3')]
analysis['h4'] = [h.text.strip() for h in soup.find_all('h4')]

# Images
images = soup.find_all('img')
analysis['total_images'] = len(images)
analysis['images_without_alt'] = len([img for img in images if not img.get('alt')])
analysis['images_without_title'] = len([img for img in images if not img.get('title')])

# Links
all_links = soup.find_all('a', href=True)
analysis['total_links'] = len(all_links)
internal_links = [a for a in all_links if not a['href'].startswith('http') or 'tln-werbemittel.de' in a['href']]
external_links = [a for a in all_links if a['href'].startswith('http') and 'tln-werbemittel.de' not in a['href']]
analysis['internal_links'] = len(internal_links)
analysis['external_links'] = len(external_links)

# Check for no-follow links
nofollow_links = [a for a in all_links if a.get('rel') and 'nofollow' in a.get('rel')]
analysis['nofollow_links'] = len(nofollow_links)

# Canonical URL
canonical = soup.find('link', {'rel': 'canonical'})
analysis['canonical_url'] = canonical.get('href') if canonical else None

# Language
html_tag = soup.find('html')
analysis['language'] = html_tag.get('lang') if html_tag else None

# Schema.org structured data
schema_scripts = soup.find_all('script', type='application/ld+json')
analysis['schema_markup_count'] = len(schema_scripts)
if schema_scripts:
    analysis['schema_types'] = []
    for script in schema_scripts:
        try:
            schema_data = json.loads(script.string)
            if '@type' in schema_data:
                analysis['schema_types'].append(schema_data['@type'])
        except:
            pass

# Open Graph tags
og_tags = {}
for meta in soup.find_all('meta', property=re.compile('^og:')):
    og_tags[meta['property']] = meta.get('content', '')
analysis['open_graph'] = og_tags

# Twitter Card tags
twitter_tags = {}
for meta in soup.find_all('meta', attrs={'name': re.compile('^twitter:')}):
    twitter_tags[meta['name']] = meta.get('content', '')
analysis['twitter_card'] = twitter_tags

# Forms
forms = soup.find_all('form')
analysis['total_forms'] = len(forms)

# Scripts
scripts = soup.find_all('script')
analysis['total_scripts'] = len(scripts)
analysis['inline_scripts'] = len([s for s in scripts if not s.get('src')])
analysis['external_scripts'] = len([s for s in scripts if s.get('src')])

# Stylesheets
stylesheets = soup.find_all('link', rel='stylesheet')
analysis['total_stylesheets'] = len(stylesheets)

# Check for viewport meta tag
viewport = soup.find('meta', attrs={'name': 'viewport'})
analysis['has_viewport'] = viewport is not None
analysis['viewport_content'] = viewport.get('content') if viewport else None

# Check for favicon
favicon = soup.find('link', rel=re.compile('icon'))
analysis['has_favicon'] = favicon is not None

# Word count (approximate)
text_content = soup.get_text()
words = text_content.split()
analysis['word_count'] = len(words)

# Print analysis
print(json.dumps(analysis, indent=2, ensure_ascii=False))

# Save to file
with open('html_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(analysis, f, indent=2, ensure_ascii=False)
