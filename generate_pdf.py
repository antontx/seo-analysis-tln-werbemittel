#!/usr/bin/env python3
import os
import markdown2
from weasyprint import HTML, CSS
from datetime import datetime

def read_markdown_file(filepath):
    """Read markdown file and return content"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def generate_pdf():
    """Generate comprehensive PDF from all markdown reports"""

    # Define the order of reports
    report_files = [
        ('SEO_Reports/SEO_Analysis_Report.md', 'Executive Summary'),
        ('SEO_Reports/Core_Web_Vitals_Report.md', 'Core Web Vitals & Performance'),
        ('SEO_Reports/Technical_SEO_Details.md', 'Technical SEO Deep Dive'),
        ('SEO_Reports/Content_SEO_Strategy.md', 'Content & SEO Strategy'),
        ('SEO_Reports/Quick_Fixes_Checklist.md', 'Implementation Checklist')
    ]

    # Start building HTML content
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>SEO Analysis Report - TLN-Werbemittel.de</title>
        <style>
            @page {
                size: A4;
                margin: 2cm;
                @bottom-center {
                    content: counter(page);
                }
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 100%;
            }

            .cover-page {
                page-break-after: always;
                text-align: center;
                padding-top: 200px;
            }

            .cover-page h1 {
                font-size: 36px;
                margin-bottom: 20px;
                color: #2c3e50;
            }

            .cover-page h2 {
                font-size: 24px;
                color: #7f8c8d;
                font-weight: normal;
            }

            .cover-page .date {
                margin-top: 100px;
                font-size: 16px;
                color: #95a5a6;
            }

            .toc {
                page-break-after: always;
            }

            .toc h2 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }

            .toc ul {
                list-style: none;
                padding-left: 0;
            }

            .toc li {
                margin: 15px 0;
                font-size: 16px;
            }

            .toc a {
                text-decoration: none;
                color: #34495e;
            }

            .toc a:hover {
                color: #3498db;
            }

            .section {
                page-break-before: always;
            }

            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                margin-top: 0;
                page-break-after: avoid;
            }

            h2 {
                color: #34495e;
                margin-top: 30px;
                page-break-after: avoid;
            }

            h3 {
                color: #7f8c8d;
                margin-top: 20px;
                page-break-after: avoid;
            }

            table {
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
                page-break-inside: avoid;
            }

            th {
                background-color: #3498db;
                color: white;
                padding: 12px;
                text-align: left;
            }

            td {
                padding: 10px;
                border-bottom: 1px solid #ecf0f1;
            }

            tr:nth-child(even) {
                background-color: #f8f9fa;
            }

            code {
                background-color: #f4f4f4;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }

            pre {
                background-color: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                page-break-inside: avoid;
            }

            pre code {
                background-color: transparent;
                padding: 0;
            }

            blockquote {
                border-left: 4px solid #3498db;
                padding-left: 20px;
                margin-left: 0;
                color: #555;
                font-style: italic;
            }

            ul, ol {
                margin-left: 20px;
            }

            li {
                margin: 5px 0;
            }

            .alert {
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
                page-break-inside: avoid;
            }

            .alert-critical {
                background-color: #ffe4e1;
                border-left: 5px solid #dc3545;
            }

            .alert-warning {
                background-color: #fff3cd;
                border-left: 5px solid #ffc107;
            }

            .alert-success {
                background-color: #d4edda;
                border-left: 5px solid #28a745;
            }

            hr {
                border: none;
                border-top: 2px solid #ecf0f1;
                margin: 30px 0;
            }

            strong {
                color: #2c3e50;
            }

            /* Emoji support */
            .emoji {
                font-size: 1.2em;
            }
        </style>
    </head>
    <body>
    """

    # Add cover page
    html_content += f"""
    <div class="cover-page">
        <h1>SEO Analysis Report</h1>
        <h2>TLN-Werbemittel.de</h2>
        <p style="font-size: 18px; margin-top: 40px;">Comprehensive SEO and Performance Analysis</p>
        <div class="date">
            <p>Generated: {datetime.now().strftime('%B %d, %Y')}</p>
            <p>Analysis Version: 1.0</p>
        </div>
    </div>
    """

    # Add table of contents
    html_content += """
    <div class="toc">
        <h2>Table of Contents</h2>
        <ul>
    """

    for i, (filepath, title) in enumerate(report_files, 1):
        html_content += f'<li>{i}. <a href="#{i}">{title}</a></li>'

    html_content += """
        </ul>
    </div>
    """

    # Process each markdown file
    for i, (filepath, title) in enumerate(report_files, 1):
        print(f"Processing: {title}")

        # Read markdown content
        md_content = read_markdown_file(filepath)

        # Convert markdown to HTML
        html_from_md = markdown2.markdown(
            md_content,
            extras=[
                'tables',
                'fenced-code-blocks',
                'header-ids',
                'strike',
                'task_list',
                'footnotes'
            ]
        )

        # Add section with anchor
        html_content += f'<div class="section" id="{i}">'

        # Replace emoji codes with actual emojis
        html_from_md = html_from_md.replace('✅', '<span class="emoji">✅</span>')
        html_from_md = html_from_md.replace('❌', '<span class="emoji">❌</span>')
        html_from_md = html_from_md.replace('⚠️', '<span class="emoji">⚠️</span>')
        html_from_md = html_from_md.replace('🔴', '<span class="emoji">🔴</span>')
        html_from_md = html_from_md.replace('🟡', '<span class="emoji">🟡</span>')
        html_from_md = html_from_md.replace('🟢', '<span class="emoji">🟢</span>')
        html_from_md = html_from_md.replace('📊', '<span class="emoji">📊</span>')
        html_from_md = html_from_md.replace('🎯', '<span class="emoji">🎯</span>')
        html_from_md = html_from_md.replace('💡', '<span class="emoji">💡</span>')
        html_from_md = html_from_md.replace('🚨', '<span class="emoji">🚨</span>')
        html_from_md = html_from_md.replace('🔥', '<span class="emoji">🔥</span>')
        html_from_md = html_from_md.replace('📈', '<span class="emoji">📈</span>')
        html_from_md = html_from_md.replace('🛠️', '<span class="emoji">🛠️</span>')
        html_from_md = html_from_md.replace('📝', '<span class="emoji">📝</span>')
        html_from_md = html_from_md.replace('🚀', '<span class="emoji">🚀</span>')
        html_from_md = html_from_md.replace('📱', '<span class="emoji">📱</span>')
        html_from_md = html_from_md.replace('⚡', '<span class="emoji">⚡</span>')
        html_from_md = html_from_md.replace('📦', '<span class="emoji">📦</span>')
        html_from_md = html_from_md.replace('🔍', '<span class="emoji">🔍</span>')
        html_from_md = html_from_md.replace('📋', '<span class="emoji">📋</span>')
        html_from_md = html_from_md.replace('✔️', '<span class="emoji">✔️</span>')
        html_from_md = html_from_md.replace('📞', '<span class="emoji">📞</span>')
        html_from_md = html_from_md.replace('💰', '<span class="emoji">💰</span>')
        html_from_md = html_from_md.replace('🆘', '<span class="emoji">🆘</span>')

        # Add critical alert styling
        if 'CRITICAL' in html_from_md:
            html_from_md = html_from_md.replace(
                '<p>🔴 CRITICAL',
                '<div class="alert alert-critical"><p>🔴 CRITICAL'
            )
            html_from_md = html_from_md.replace(
                'CRITICAL FAILURE',
                'CRITICAL FAILURE</p></div><p>'
            )

        html_content += html_from_md
        html_content += '</div>'

    # Close HTML
    html_content += """
    </body>
    </html>
    """

    # Generate PDF
    print("\nGenerating PDF...")
    pdf_path = 'SEO_Analysis_Complete_Report.pdf'

    # Create PDF with WeasyPrint
    HTML(string=html_content).write_pdf(pdf_path)

    print(f"✅ PDF generated successfully: {pdf_path}")

    # Get file size
    file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # Convert to MB
    print(f"📄 File size: {file_size:.2f} MB")

    return pdf_path

if __name__ == "__main__":
    generate_pdf()
