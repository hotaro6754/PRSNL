import os
import time
from playwright.sync_api import sync_playwright

BASE_DIR = r"E:\sih26145-prototype"
DOCS_DIR = os.path.join(BASE_DIR, r"ps26145-docs\docs\handbook")
OUT_MD = os.path.join(BASE_DIR, "PS26145_Technical_Handbook.md")
OUT_HTML = os.path.join(BASE_DIR, "PS26145_Technical_Handbook.html")
OUT_PDF = os.path.join(BASE_DIR, "PS26145_Technical_Handbook.pdf")

def build():
    # 1. Combine Markdown
    print("Combining Markdown Volumes...")
    files = sorted([f for f in os.listdir(DOCS_DIR) if f.endswith('.md')])
    
    combined_md = "# PS26145 Technical Handbook\n\n"
    combined_md += "*A fully detailed, 50-chapter technical publication built from scratch.*\n\n---\n\n"
    
    for filename in files:
        with open(os.path.join(DOCS_DIR, filename), "r", encoding="utf-8") as f:
            content = f.read()
            # Fix image paths if necessary
            content = content.replace("../../assets/screenshots", "./ps26145-docs/docs/assets/screenshots")
            combined_md += content + "\n\n---\n\n"

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(combined_md)
    print(f"Generated {OUT_MD}")

    # 2. Wrap in HTML with Markdown, Mermaid, and MathJax renderers
    print("Generating HTML Wrapper...")
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PS26145 Technical Handbook</title>
    <!-- Marked.js for Markdown parsing -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <!-- Mermaid.js for Diagrams -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <!-- MathJax for LaTeX -->
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px;
        }}
        h1, h2, h3 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; page-break-after: avoid; }}
        h1 {{ font-size: 2.5em; text-align: center; margin-bottom: 40px; border-bottom: 2px solid #2c3e50; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; page-break-inside: avoid; }}
        code {{ font-family: Consolas, Monaco, monospace; background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
        img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); page-break-inside: avoid; }}
        .mermaid {{ text-align: center; margin: 20px 0; page-break-inside: avoid; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; page-break-inside: avoid; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f8f9fa; }}
        hr {{ border: 0; border-top: 1px solid #eee; margin: 40px 0; }}
        .page-break {{ page-break-before: always; }}
    </style>
</head>
<body>
    <div id="content"></div>
    <textarea id="markdown-source" style="display:none;">{combined_md}</textarea>
    
    <script>
        // Custom renderer to support Mermaid blocks
        const renderer = new marked.Renderer();
        const originalCodeRenderer = renderer.code.bind(renderer);
        renderer.code = function(code, language, isEscaped) {{
            if (language === 'mermaid') {{
                return '<div class="mermaid">' + code + '</div>';
            }}
            return originalCodeRenderer(code, language, isEscaped);
        }};
        
        marked.setOptions({{ renderer: renderer }});
        
        // Render Markdown to HTML
        document.getElementById('content').innerHTML = marked.parse(document.getElementById('markdown-source').value);
        
        // Initialize Mermaid
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
</body>
</html>
"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"Generated {OUT_HTML}")

    # 3. Print to PDF via Playwright
    print("Printing to PDF via Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Load local HTML file
        page.goto(f"file://{OUT_HTML}", wait_until="networkidle")
        
        # Wait a moment for MathJax and Mermaid to fully render
        page.wait_for_timeout(3000) 
        
        page.pdf(
            path=OUT_PDF,
            format="A4",
            margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"},
            print_background=True,
            display_header_footer=True,
            header_template="<div style='font-size: 10px; width: 100%; text-align: center; color: #888;'>PS26145 Technical Handbook</div>",
            footer_template="<div style='font-size: 10px; width: 100%; text-align: center; color: #888;'><span class='pageNumber'></span> / <span class='totalPages'></span></div>"
        )
        browser.close()
    
    print(f"Generated PDF successfully: {OUT_PDF}")

if __name__ == "__main__":
    build()
