#!/usr/bin/env python3
import requests
import time
import json
from urllib.parse import urlparse

def check_performance(url):
    """Check website performance metrics"""
    results = {}

    # Test response times with multiple requests
    response_times = []
    for i in range(3):
        start = time.time()
        response = requests.get(url, timeout=30)
        end = time.time()
        response_times.append(end - start)
        time.sleep(1)

    results['avg_response_time'] = sum(response_times) / len(response_times)
    results['min_response_time'] = min(response_times)
    results['max_response_time'] = max(response_times)

    # Check page size
    response = requests.get(url)
    results['page_size_bytes'] = len(response.content)
    results['page_size_kb'] = results['page_size_bytes'] / 1024

    # Check compression
    results['content_encoding'] = response.headers.get('Content-Encoding', 'None')
    results['uses_compression'] = 'gzip' in results['content_encoding'] or 'br' in results['content_encoding']

    # Check caching headers
    cache_headers = {}
    cache_headers['cache_control'] = response.headers.get('Cache-Control', 'Not set')
    cache_headers['expires'] = response.headers.get('Expires', 'Not set')
    cache_headers['etag'] = response.headers.get('ETag', 'Not set')
    cache_headers['last_modified'] = response.headers.get('Last-Modified', 'Not set')
    results['cache_headers'] = cache_headers

    # Check security headers
    security_headers = {}
    security_headers['strict_transport_security'] = response.headers.get('Strict-Transport-Security', 'Not set')
    security_headers['x_content_type_options'] = response.headers.get('X-Content-Type-Options', 'Not set')
    security_headers['x_frame_options'] = response.headers.get('X-Frame-Options', 'Not set')
    security_headers['x_xss_protection'] = response.headers.get('X-XSS-Protection', 'Not set')
    security_headers['content_security_policy'] = response.headers.get('Content-Security-Policy', 'Not set')
    results['security_headers'] = security_headers

    # Check HTTP/2
    results['http_version'] = 'HTTP/2' if response.raw.version == 20 else f'HTTP/{response.raw.version/10}'

    # Check server
    results['server'] = response.headers.get('Server', 'Not disclosed')

    # Check for CDN
    results['cdn'] = 'cloudflare' in response.headers.get('Server', '').lower() or 'CF-RAY' in response.headers

    return results

def check_pagespeed_insights(url):
    """Use Google PageSpeed Insights API"""
    api_key = 'AIzaSyDkEX-f1JNLQLC164SZaobALqFv4PHV-kA'  # Free tier key for testing
    api_url = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'

    results = {}

    for strategy in ['mobile', 'desktop']:
        params = {
            'url': url,
            'strategy': strategy,
            'category': ['performance', 'accessibility', 'seo', 'best-practices']
        }

        try:
            response = requests.get(api_url, params=params, timeout=60)
            if response.status_code == 200:
                data = response.json()

                lighthouse = data.get('lighthouseResult', {})
                categories = lighthouse.get('categories', {})

                results[strategy] = {
                    'performance_score': categories.get('performance', {}).get('score', 0) * 100,
                    'accessibility_score': categories.get('accessibility', {}).get('score', 0) * 100,
                    'seo_score': categories.get('seo', {}).get('score', 0) * 100,
                    'best_practices_score': categories.get('best-practices', {}).get('score', 0) * 100
                }

                # Core Web Vitals
                audits = lighthouse.get('audits', {})
                results[strategy]['core_web_vitals'] = {
                    'first_contentful_paint': audits.get('first-contentful-paint', {}).get('displayValue', 'N/A'),
                    'largest_contentful_paint': audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A'),
                    'cumulative_layout_shift': audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A'),
                    'total_blocking_time': audits.get('total-blocking-time', {}).get('displayValue', 'N/A'),
                    'speed_index': audits.get('speed-index', {}).get('displayValue', 'N/A')
                }
        except Exception as e:
            results[strategy] = {'error': str(e)}

    return results

if __name__ == "__main__":
    url = "https://www.tln-werbemittel.de"

    print("Checking performance metrics...")
    perf_results = check_performance(url)

    print("\nPerformance Results:")
    print(json.dumps(perf_results, indent=2))

    print("\nChecking PageSpeed Insights (this may take a minute)...")
    pagespeed_results = check_pagespeed_insights(url)

    print("\nPageSpeed Insights Results:")
    print(json.dumps(pagespeed_results, indent=2))

    # Save results
    all_results = {
        'performance_metrics': perf_results,
        'pagespeed_insights': pagespeed_results
    }

    with open('performance_analysis.json', 'w') as f:
        json.dump(all_results, f, indent=2)
