import os
import html
import base64

BASE_DIR = r"E:\cyberos-prototype\educational_dashboard"
RAW_MODULES_DIR = os.path.join(BASE_DIR, "raw_modules")
DIAGRAMS_DIR = r"E:\cyberos-prototype\presentation\diagrams"
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "screenshots")

OUT_HTML = os.path.join(BASE_DIR, "CyberOS_Master_Course.html")
OUT_MD = os.path.join(BASE_DIR, "CyberOS_Master_Course.md")

def get_base64_file(filepath, mimetype):
    try:
        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mimetype};base64,{encoded}"
    except Exception:
        return ""

def process_html_diagrams():
    diagrams = []
    if not os.path.exists(DIAGRAMS_DIR): return diagrams
    for filename in sorted(os.listdir(DIAGRAMS_DIR)):
        if filename.endswith(".html") and filename != "index.html":
            try:
                with open(os.path.join(DIAGRAMS_DIR, filename), "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                diagrams.append({
                    "name": filename.replace(".html", ""), 
                    "b64": encoded
                })
            except Exception: pass
    return diagrams

def build():
    print("Aggregating 53 modules into Master Book...")
    
    diagrams = process_html_diagrams()
    master_md = "# CyberOS: Passive Threat Detection Master Course\n\n"
    master_md += "## System Architecture Gallery\n\n"
    
    for diag in diagrams:
        master_md += f"### {diag['name'].replace('_', ' ').title()}\n"
        # Switched to zoom: 0.55 which Chrome's print spooler respects natively without breaking bounding boxes
        master_md += f'''<div style="margin-bottom: 50px; background: white; page-break-inside: avoid; border: 1px solid #ddd; border-radius: 8px;">
            <iframe src="data:text/html;base64,{diag['b64']}" style="width: 1600px; height: 900px; zoom: 0.55; border: none; background: transparent; display: block;" scrolling="no"></iframe>
        </div>\n\n'''
    
    master_md += "<div style='page-break-after: always;'></div>\n\n"
    
    e2e_base64 = get_base64_file(os.path.join(ASSETS_DIR, "e2e_full_dashboard.png"), "image/png")
    
    if os.path.exists(RAW_MODULES_DIR):
        for filename in sorted(os.listdir(RAW_MODULES_DIR)):
            if filename.endswith(".md"):
                with open(os.path.join(RAW_MODULES_DIR, filename), "r", encoding="utf-8") as f:
                    content = f.read()
                    if e2e_base64:
                        content = content.replace("assets/screenshots/e2e_full_dashboard.png", e2e_base64)
                        content = content.replace("../assets/screenshots/e2e_full_dashboard.png", e2e_base64)
                    
                    master_md += content + "\n\n<div style='page-break-after: always;'></div>\n\n"
    
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(master_md)
    print(f"Generated Raw Markdown: {OUT_MD}")
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CyberOS Master Course</title>
    <script src="https://cdn.jsdelivr.net/npm/marked@4.3.0/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; line-height: 1.6; color: #333; max-width: 1000px; margin: 0 auto; padding: 40px; background: #fff; }}
        h1 {{ border-bottom: 3px solid #27ae60; padding-bottom: 10px; color: #2c3e50; font-size: 2.5em; }}
        h2 {{ color: #2980b9; margin-top: 2em; }}
        pre {{ background: #282c34; color: #abb2bf; padding: 15px; border-radius: 6px; overflow-x: auto; box-shadow: none !important; }}
        code {{ font-family: 'Consolas', monospace; }}
        img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
        .mermaid {{ display: flex; justify-content: center; margin: 30px 0; }}
        .mermaid-error {{ color: red; border: 1px solid red; padding: 10px; }}
        
        #loading-overlay {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(255, 255, 255, 0.95); z-index: 9999;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }}
        #loading-text {{ font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px; }}
        
        @media print {{
            body {{ padding: 0; max-width: 100%; background: white; }}
            .no-print {{ display: none !important; }}
            pre, blockquote, .mermaid, iframe, img, .box {{ page-break-inside: avoid !important; }}
            h1, h2, h3, h4 {{ page-break-after: avoid !important; }}
            iframe {{ display: block; max-width: 100%; }}
        }}
        .print-btn {{
            position: fixed; top: 20px; right: 20px; background: #27ae60; color: white; border: none; 
            padding: 15px 25px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            z-index: 10000;
        }}
        .print-btn:hover {{ background: #219653; transform: scale(1.05); }}
    </style>
</head>
<body>
    <div id="loading-overlay" class="no-print">
        <div id="loading-text">Loading 150KB textbook and rendering 53 charts... Please wait...</div>
        <div style="color: #666;">Do not print until this disappears.</div>
    </div>

    <button id="btn-print" class="print-btn no-print" style="display: none;" onclick="window.print()">🖨️ Save as PDF</button>
    <div id="content"></div>

    <script id="markdown-data" type="text/markdown">{master_md}</script>

    <script>
        mermaid.initialize({{ startOnLoad: false, theme: 'default', suppressErrorRendering: true }});
        
        const renderer = new marked.Renderer();
        const originalCodeRenderer = renderer.code.bind(renderer);
        renderer.code = function(code, language, isEscaped) {{
            if (language === 'mermaid') return '<div class="mermaid">' + code + '</div>';
            return originalCodeRenderer(code, language, isEscaped);
        }};
        
        marked.setOptions({{
            renderer: renderer,
            highlight: function(code, lang) {{
                if (lang && hljs.getLanguage(lang)) return hljs.highlight(code, {{ language: lang }}).value;
                return hljs.highlightAuto(code).value;
            }}
        }});
        
        async function renderMermaidAsync() {{
            const nodes = document.querySelectorAll('.mermaid');
            for (let i = 0; i < nodes.length; i++) {{
                const node = nodes[i];
                node.removeAttribute('data-processed');
                const id = 'mermaid-svg-' + Math.random().toString(36).substr(2, 9);
                try {{
                    const {{ svg }} = await mermaid.render(id, node.textContent);
                    node.innerHTML = svg;
                }} catch (e) {{
                    console.warn("Mermaid error:", e);
                    node.innerHTML = `<div class="mermaid-error">⚠️ Mermaid Syntax Error</div><pre><code>${{node.textContent}}</code></pre>`;
                }}
            }}
        }}
        
        window.onload = function() {{
            // 1. Parse Markdown
            const mdContent = document.getElementById('markdown-data').textContent;
            document.getElementById('content').innerHTML = marked.parse(mdContent);
            
            // 2. Render Mermaid Charts
            renderMermaidAsync().then(() => {{
                // 3. Typeset Math
                if (window.MathJax) {{
                    MathJax.typesetPromise().then(finishLoading);
                }} else {{
                    finishLoading();
                }}
            }}).catch(finishLoading); // Fail gracefully
            
            function finishLoading() {{
                document.getElementById('loading-overlay').style.display = 'none';
                document.getElementById('btn-print').style.display = 'block';
            }}
        }};
    </script>
</body>
</html>
"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_template.strip())
    print(f"Generated Printable Book: {OUT_HTML}")

if __name__ == "__main__":
    build()
