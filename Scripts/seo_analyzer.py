#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, urljoin
import time
import dns.resolver
import whois
from datetime import datetime
import ssl
import socket

class SEOAnalyzer:
    def __init__(self, url):
        self.url = url
        self.domain = urlparse(url).netloc
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def analyze_page(self):
        print(f"Analyzing {self.url}...")
        response = self.session.get(self.url, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')

        analysis = {
            'url': self.url,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'page_size': len(response.content),
            'encoding': response.encoding,
        }

        # Meta tags
        analysis['title'] = soup.find('title').text if soup.find('title') else None
        analysis['title_length'] = len(analysis['title']) if analysis['title'] else 0

        meta_desc = soup.find('meta', attrs={'name': 'description'})
        analysis['meta_description'] = meta_desc.get('content') if meta_desc else None
        analysis['meta_description_length'] = len(analysis['meta_description']) if analysis['meta_description'] else 0

        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        analysis['meta_keywords'] = meta_keywords.get('content') if meta_keywords else None

        # Canonical URL
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        analysis['canonical_url'] = canonical.get('href') if canonical else None

        # Language
        analysis['language'] = soup.find('html').get('lang') if soup.find('html') else None

        # Headings
        analysis['h1_tags'] = [h1.text.strip() for h1 in soup.find_all('h1')]
        analysis['h2_tags'] = [h2.text.strip() for h2 in soup.find_all('h2')]
        analysis['h3_tags'] = [h3.text.strip() for h3 in soup.find_all('h3')]

        # Images
        images = soup.find_all('img')
        analysis['total_images'] = len(images)
        analysis['images_without_alt'] = len([img for img in images if not img.get('alt')])

        # Links
        links = soup.find_all('a', href=True)
        internal_links = []
        external_links = []

        for link in links:
            href = link['href']
            if href.startswith('http'):
                if self.domain in href:
                    internal_links.append(href)
                else:
                    external_links.append(href)
            elif href.startswith('/'):
                internal_links.append(urljoin(self.url, href))

        analysis['internal_links'] = len(internal_links)
        analysis['external_links'] = len(external_links)
        analysis['total_links'] = len(links)

        # Open Graph tags
        og_tags = {}
        for tag in soup.find_all('meta', property=True):
            if tag['property'].startswith('og:'):
                og_tags[tag['property']] = tag.get('content')
        analysis['open_graph_tags'] = og_tags

        # Schema markup
        schema_scripts = soup.find_all('script', type='application/ld+json')
        analysis['schema_markup_count'] = len(schema_scripts)

        # Mobile viewport
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        analysis['viewport_meta'] = viewport.get('content') if viewport else None

        return analysis

    def check_robots_txt(self):
        robots_url = f"https://{self.domain}/robots.txt"
        try:
            response = self.session.get(robots_url, timeout=5)
            return {
                'exists': response.status_code == 200,
                'content': response.text if response.status_code == 200 else None
            }
        except:
            return {'exists': False, 'content': None}

    def check_sitemap(self):
        sitemap_urls = [
            f"https://{self.domain}/sitemap.xml",
            f"https://{self.domain}/sitemap_index.xml",
            f"https://{self.domain}/export/sitemap_de.xml"
        ]

        sitemaps = []
        for url in sitemap_urls:
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    sitemaps.append({
                        'url': url,
                        'exists': True,
                        'size': len(response.content)
                    })
            except:
                pass

        return sitemaps

    def check_ssl(self):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    return {
                        'ssl_enabled': True,
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'expires': cert['notAfter']
                    }
        except:
            return {'ssl_enabled': False}

    def check_dns(self):
        try:
            dns_info = {}

            # A records
            a_records = dns.resolver.resolve(self.domain, 'A')
            dns_info['a_records'] = [str(r) for r in a_records]

            # MX records
            try:
                mx_records = dns.resolver.resolve(self.domain, 'MX')
                dns_info['mx_records'] = [str(r.exchange) for r in mx_records]
            except:
                dns_info['mx_records'] = []

            # TXT records
            try:
                txt_records = dns.resolver.resolve(self.domain, 'TXT')
                dns_info['txt_records'] = [str(r) for r in txt_records]
            except:
                dns_info['txt_records'] = []

            return dns_info
        except Exception as e:
            return {'error': str(e)}

    def check_domain_info(self):
        try:
            domain_info = whois.whois(self.domain)
            return {
                'registrar': domain_info.registrar,
                'creation_date': str(domain_info.creation_date) if domain_info.creation_date else None,
                'expiration_date': str(domain_info.expiration_date) if domain_info.expiration_date else None,
                'name_servers': domain_info.name_servers if hasattr(domain_info, 'name_servers') else None
            }
        except Exception as e:
            return {'error': str(e)}

    def analyze_multiple_pages(self, urls):
        results = []
        for url in urls:
            try:
                self.url = url
                results.append(self.analyze_page())
                time.sleep(1)  # Be polite
            except Exception as e:
                results.append({'url': url, 'error': str(e)})
        return results

    def run_full_analysis(self):
        print("Starting comprehensive SEO analysis...")

        report = {
            'timestamp': datetime.now().isoformat(),
            'domain': self.domain,
            'homepage_analysis': self.analyze_page(),
            'robots_txt': self.check_robots_txt(),
            'sitemaps': self.check_sitemap(),
            'ssl_certificate': self.check_ssl(),
            'dns_records': self.check_dns(),
            'domain_info': self.check_domain_info()
        }

        # Check a few more important pages
        additional_urls = [
            f"https://{self.domain}/impressum",
            f"https://{self.domain}/datenschutz",
            f"https://{self.domain}/kontakt"
        ]

        print("Analyzing additional pages...")
        report['additional_pages'] = self.analyze_multiple_pages(additional_urls)

        return report

if __name__ == "__main__":
    analyzer = SEOAnalyzer("https://www.tln-werbemittel.de")
    report = analyzer.run_full_analysis()

    # Save report
    with open('seo_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\nAnalysis complete! Report saved to seo_analysis_report.json")

    # Print summary
    print("\n=== SUMMARY ===")
    home = report['homepage_analysis']
    print(f"Title: {home.get('title')}")
    print(f"Title Length: {home.get('title_length')} chars")
    print(f"Meta Description Length: {home.get('meta_description_length')} chars")
    print(f"H1 Tags: {len(home.get('h1_tags', []))}")
    print(f"Images without ALT: {home.get('images_without_alt')} / {home.get('total_images')}")
    print(f"SSL: {report['ssl_certificate'].get('ssl_enabled')}")
    print(f"Robots.txt: {report['robots_txt'].get('exists')}")
    print(f"Sitemaps found: {len(report.get('sitemaps', []))}")
