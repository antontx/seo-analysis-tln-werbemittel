#!/usr/bin/env python3
import json
import requests
import time

def analyze_lighthouse_report():
    """Analyze the local Lighthouse report"""
    try:
        with open('lighthouse-report.json', 'r') as f:
            data = json.load(f)

        print("=" * 60)
        print("LIGHTHOUSE PERFORMANCE ANALYSIS")
        print("=" * 60)

        # Categories scores
        categories = data.get('categories', {})

        print("\n📊 OVERALL SCORES (0-100):")
        print("-" * 40)
        for category, details in categories.items():
            score = details.get('score', 0) * 100 if details.get('score') else 0
            title = details.get('title', category)

            # Color coding
            if score >= 90:
                indicator = "🟢"
            elif score >= 50:
                indicator = "🟡"
            else:
                indicator = "🔴"

            print(f"{indicator} {title}: {score:.0f}/100")

        # Core Web Vitals
        audits = data.get('audits', {})

        print("\n⚡ CORE WEB VITALS:")
        print("-" * 40)

        # First Contentful Paint
        fcp = audits.get('first-contentful-paint', {})
        if fcp:
            print(f"First Contentful Paint (FCP): {fcp.get('displayValue', 'N/A')}")
            print(f"  Score: {fcp.get('score', 0) * 100:.0f}/100")

        # Largest Contentful Paint
        lcp = audits.get('largest-contentful-paint', {})
        if lcp:
            print(f"\nLargest Contentful Paint (LCP): {lcp.get('displayValue', 'N/A')}")
            print(f"  Score: {lcp.get('score', 0) * 100:.0f}/100")

        # Cumulative Layout Shift
        cls = audits.get('cumulative-layout-shift', {})
        if cls:
            print(f"\nCumulative Layout Shift (CLS): {cls.get('displayValue', 'N/A')}")
            print(f"  Score: {cls.get('score', 0) * 100:.0f}/100")

        # Total Blocking Time
        tbt = audits.get('total-blocking-time', {})
        if tbt:
            print(f"\nTotal Blocking Time (TBT): {tbt.get('displayValue', 'N/A')}")
            print(f"  Score: {tbt.get('score', 0) * 100:.0f}/100")

        # Speed Index
        si = audits.get('speed-index', {})
        if si:
            print(f"\nSpeed Index: {si.get('displayValue', 'N/A')}")
            print(f"  Score: {si.get('score', 0) * 100:.0f}/100")

        # Time to Interactive
        tti = audits.get('interactive', {})
        if tti:
            print(f"\nTime to Interactive (TTI): {tti.get('displayValue', 'N/A')}")
            print(f"  Score: {tti.get('score', 0) * 100:.0f}/100")

        print("\n📈 PERFORMANCE METRICS:")
        print("-" * 40)

        # Other important metrics
        metrics_to_check = [
            ('first-meaningful-paint', 'First Meaningful Paint'),
            ('max-potential-fid', 'Max Potential First Input Delay'),
            ('server-response-time', 'Server Response Time'),
            ('mainthread-work-breakdown', 'Main Thread Work'),
            ('bootup-time', 'JavaScript Execution Time'),
            ('uses-responsive-images', 'Responsive Images'),
            ('uses-optimized-images', 'Optimized Images'),
            ('uses-webp-images', 'WebP Images'),
            ('uses-text-compression', 'Text Compression'),
            ('uses-rel-preconnect', 'Preconnect'),
            ('font-display', 'Font Display'),
            ('third-party-summary', 'Third-party Impact')
        ]

        for audit_id, name in metrics_to_check:
            audit = audits.get(audit_id, {})
            if audit:
                score = audit.get('score', 0) * 100 if audit.get('score') is not None else None
                value = audit.get('displayValue', '')
                if score is not None:
                    status = "✅" if score >= 90 else "⚠️" if score >= 50 else "❌"
                    print(f"{status} {name}: {value} (Score: {score:.0f})")
                elif value:
                    print(f"   {name}: {value}")

        # Opportunities
        print("\n💡 IMPROVEMENT OPPORTUNITIES:")
        print("-" * 40)

        opportunities = []
        for audit_id, audit in audits.items():
            if audit.get('details', {}).get('type') == 'opportunity':
                if audit.get('score', 1) < 0.9:
                    saving = audit.get('details', {}).get('overallSavingsMs', 0)
                    opportunities.append((saving, audit.get('title'), audit.get('displayValue', '')))

        opportunities.sort(reverse=True)
        for i, (saving, title, value) in enumerate(opportunities[:10], 1):
            if saving > 0:
                print(f"{i}. {title}")
                print(f"   Potential saving: {saving:.0f}ms {value}")

        # Diagnostics
        print("\n🔍 DIAGNOSTICS:")
        print("-" * 40)

        diagnostics = []
        diagnostic_audits = [
            'largest-contentful-paint-element',
            'layout-shift-elements',
            'long-tasks',
            'non-composited-animations',
            'uses-passive-event-listeners',
            'no-document-write',
            'dom-size'
        ]

        for audit_id in diagnostic_audits:
            audit = audits.get(audit_id, {})
            score = audit.get('score') if audit else None
            if audit and score is not None and score < 1:
                diagnostics.append(f"⚠️ {audit.get('title', audit_id)}: {audit.get('displayValue', '')}")

        for diagnostic in diagnostics:
            print(diagnostic)

        # Resource summary
        print("\n📦 RESOURCE SUMMARY:")
        print("-" * 40)

        network_requests = audits.get('network-requests', {})
        if network_requests and network_requests.get('details'):
            items = network_requests['details'].get('items', [])
            print(f"Total requests: {len(items)}")

            total_size = sum(item.get('transferSize', 0) for item in items)
            print(f"Total transfer size: {total_size / 1024 / 1024:.2f} MB")

            # Group by resource type
            resource_types = {}
            for item in items:
                resource_type = item.get('resourceType', 'Other')
                if resource_type not in resource_types:
                    resource_types[resource_type] = {'count': 0, 'size': 0}
                resource_types[resource_type]['count'] += 1
                resource_types[resource_type]['size'] += item.get('transferSize', 0)

            print("\nBy resource type:")
            for rtype, data in sorted(resource_types.items(), key=lambda x: x[1]['size'], reverse=True):
                size_mb = data['size'] / 1024 / 1024
                print(f"  {rtype}: {data['count']} requests, {size_mb:.2f} MB")

        return data

    except FileNotFoundError:
        print("Lighthouse report not found. Generating...")
        return None
    except json.JSONDecodeError:
        print("Error parsing Lighthouse report")
        return None

def check_pagespeed_insights(url):
    """Check Google PageSpeed Insights"""
    print("\n" + "=" * 60)
    print("GOOGLE PAGESPEED INSIGHTS")
    print("=" * 60)

    # Using the PageSpeed Insights API
    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    for strategy in ['mobile', 'desktop']:
        print(f"\n📱 {strategy.upper()} RESULTS:")
        print("-" * 40)

        params = {
            'url': url,
            'strategy': strategy,
            'category': ['performance', 'accessibility', 'best-practices', 'seo']
        }

        try:
            print(f"Analyzing {strategy} performance... (this may take 30-60 seconds)")
            response = requests.get(api_url, params=params, timeout=60)

            if response.status_code == 200:
                data = response.json()
                lighthouse = data.get('lighthouseResult', {})

                # Categories
                categories = lighthouse.get('categories', {})
                for cat_id, cat_data in categories.items():
                    score = cat_data.get('score', 0) * 100
                    title = cat_data.get('title', cat_id)

                    if score >= 90:
                        indicator = "🟢"
                    elif score >= 50:
                        indicator = "🟡"
                    else:
                        indicator = "🔴"

                    print(f"{indicator} {title}: {score:.0f}/100")

                # Core Web Vitals
                audits = lighthouse.get('audits', {})
                print(f"\nCore Web Vitals ({strategy}):")

                cwv_metrics = [
                    ('first-contentful-paint', 'FCP'),
                    ('largest-contentful-paint', 'LCP'),
                    ('cumulative-layout-shift', 'CLS'),
                    ('total-blocking-time', 'TBT'),
                    ('speed-index', 'Speed Index'),
                    ('interactive', 'TTI')
                ]

                for audit_id, label in cwv_metrics:
                    audit = audits.get(audit_id, {})
                    if audit:
                        value = audit.get('displayValue', 'N/A')
                        score = audit.get('score', 0) * 100
                        status = "✅" if score >= 90 else "⚠️" if score >= 50 else "❌"
                        print(f"  {status} {label}: {value}")

                # Field data (if available)
                loading_experience = data.get('loadingExperience', {})
                if loading_experience.get('metrics'):
                    print(f"\n📊 Real User Data (Field Data):")
                    metrics = loading_experience['metrics']

                    if 'FIRST_CONTENTFUL_PAINT_MS' in metrics:
                        fcp_data = metrics['FIRST_CONTENTFUL_PAINT_MS']
                        print(f"  FCP (P75): {fcp_data.get('percentile', 'N/A')}ms")

                    if 'LARGEST_CONTENTFUL_PAINT_MS' in metrics:
                        lcp_data = metrics['LARGEST_CONTENTFUL_PAINT_MS']
                        print(f"  LCP (P75): {lcp_data.get('percentile', 'N/A')}ms")

                    if 'CUMULATIVE_LAYOUT_SHIFT_SCORE' in metrics:
                        cls_data = metrics['CUMULATIVE_LAYOUT_SHIFT_SCORE']
                        cls_value = cls_data.get('percentile', 0) / 100
                        print(f"  CLS (P75): {cls_value:.3f}")

                    if 'FIRST_INPUT_DELAY_MS' in metrics:
                        fid_data = metrics['FIRST_INPUT_DELAY_MS']
                        print(f"  FID (P75): {fid_data.get('percentile', 'N/A')}ms")

            else:
                print(f"Error: Unable to fetch PageSpeed data (Status: {response.status_code})")

        except requests.RequestException as e:
            print(f"Error connecting to PageSpeed Insights: {e}")
        except Exception as e:
            print(f"Error processing data: {e}")

        time.sleep(2)  # Rate limiting

if __name__ == "__main__":
    url = "https://www.tln-werbemittel.de"

    # Analyze local Lighthouse report
    lighthouse_data = analyze_lighthouse_report()

    # Check PageSpeed Insights
    check_pagespeed_insights(url)

    # Summary and recommendations
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY & RECOMMENDATIONS")
    print("=" * 60)

    print("""
Priority Actions for Core Web Vitals:

🔴 CRITICAL (Affects user experience):
1. Reduce JavaScript execution time (currently blocking)
2. Optimize images (use WebP, lazy loading)
3. Minimize layout shifts (set dimensions for images/ads)
4. Reduce server response time

🟡 IMPORTANT (Performance gains):
1. Enable text compression (gzip/brotli)
2. Preconnect to required origins
3. Remove unused CSS/JavaScript
4. Implement efficient cache policy

🟢 NICE TO HAVE (Further optimization):
1. Use resource hints (prefetch, preload)
2. Minimize main thread work
3. Reduce third-party impact
4. Implement service worker for offline
    """)
