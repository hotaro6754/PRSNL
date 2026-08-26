import os
import json
import base64

BASE_DIR = r"E:\sih26145-prototype\educational_dashboard"
RAW_MODULES_DIR = os.path.join(BASE_DIR, "raw_modules")
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "screenshots")
DIAGRAMS_DIR = r"E:\sih26145-prototype\presentation\diagrams"
INDEX_PATH = os.path.join(BASE_DIR, "index.html")

os.makedirs(ASSETS_DIR, exist_ok=True)

def get_base64_file(filepath, mimetype):
    try:
        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mimetype};base64,{encoded}"
    except Exception as e:
        print(f"Warning: Could not encode {filepath}. Error: {e}")
        return ""

def process_html_diagrams():
    """Converts the interactive HTML diagrams into Base64 data URIs."""
    diagrams = []
    if not os.path.exists(DIAGRAMS_DIR):
        return diagrams

    for filename in sorted(os.listdir(DIAGRAMS_DIR)):
        if filename.endswith(".html") and filename != "index.html":
            html_path = os.path.join(DIAGRAMS_DIR, filename)
            try:
                with open(html_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                diagrams.append({
                    "name": filename.replace(".html", ""), 
                    "b64": encoded
                })
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
    return diagrams

def build_dashboard():
    print("Compiling Educational Dashboard...")
    
    # 1. Gather all diagram iframes
    diagrams = process_html_diagrams()
    
    # Generate Main Page Content (Gallery)
    main_page_html = f"""
        <div class="content-container">
            <h1>PS26145 Master Architecture Gallery</h1>
            <p style="font-size: 1.1em; color: #555;">Welcome to the PS26145 Educational Dashboard. Below are the core architectural and systemic diagrams. Select a module from the left sidebar to dive into the technical details.</p>
            <hr style="border: 1px solid #eee; margin: 30px 0;">
    """
    
    for diag in diagrams:
        title = diag['name'].replace('_', ' ').title()
        # The CSS scale hack converts a 1600x900 canvas into an 880x495 seamless block.
        # We use a Base64 data URI in the src attribute for 100% reliable loading.
        main_page_html += f"""
        <h3>{title}</h3>
        <div style="width: 100%; max-width: 880px; height: 495px; overflow: hidden; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 50px; background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <iframe src="data:text/html;base64,{diag['b64']}" style="width: 1600px; height: 900px; transform: scale(0.55); transform-origin: 0 0; border: none; background: transparent;" scrolling="no"></iframe>
        </div>
        """
    main_page_html += "</div>"

    # 2. Extract E2E Screenshot
    e2e_screenshot_path = os.path.join(ASSETS_DIR, "e2e_full_dashboard.png")
    e2e_base64 = get_base64_file(e2e_screenshot_path, "image/png")
    
    modules_data = {}
    modules_list = []

    # 3. Read all 53 generated modules
    if os.path.exists(RAW_MODULES_DIR):
        for filename in sorted(os.listdir(RAW_MODULES_DIR)):
            if filename.endswith(".md"):
                mod_id_str = filename.replace("module_", "").replace(".md", "")
                
                with open(os.path.join(RAW_MODULES_DIR, filename), "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    if e2e_base64:
                        content = content.replace("assets/screenshots/e2e_full_dashboard.png", e2e_base64)
                        content = content.replace("../assets/screenshots/e2e_full_dashboard.png", e2e_base64)
                    
                    title = f"Module {mod_id_str}"
                    for line in content.splitlines():
                        line = line.strip()
                        if line.startswith('#'):
                            title = line.replace('#', '').strip()
                            break
                    
                    modules_data[mod_id_str] = content
                    modules_list.append({ "id": mod_id_str, "name": title })

    # 4. Serialize to JSON
    modules_json_string = json.dumps(modules_data)
    modules_list_json = json.dumps(modules_list)

    # 5. Build HTML
    html_output = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PS26145 Educational Dashboard</title>
    <!-- Marked.js for Markdown -->
    <script src="https://cdn.jsdelivr.net/npm/marked@4.3.0/marked.min.js"></script>
    <!-- Highlight.js -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
    <!-- Mermaid.js -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <!-- MathJax -->
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    
    <style>
        :root {{
            --bg-color: #f4f5f7;
            --sidebar-bg: #2c3e50;
            --sidebar-hover: #34495e;
            --text-color: #333;
            --accent: #27ae60;
            --code-bg: #282c34;
        }}
        body {{ margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; height: 100vh; background-color: var(--bg-color); color: var(--text-color); }}
        #sidebar {{ width: 350px; background-color: var(--sidebar-bg); color: #fff; overflow-y: auto; display: flex; flex-direction: column; flex-shrink: 0; }}
        .sidebar-header {{ padding: 20px; background: #1a252f; font-size: 1.2rem; font-weight: bold; text-align: center; cursor: pointer; transition: background 0.2s; }}
        .sidebar-header:hover {{ background: #27ae60; }}
        .module-link {{ padding: 12px 20px; cursor: pointer; border-bottom: 1px solid #34495e; transition: background 0.2s; font-size: 0.90rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .module-link:hover {{ background-color: var(--sidebar-hover); border-left: 4px solid var(--accent); }}
        .module-link.active {{ background-color: var(--sidebar-hover); border-left: 4px solid var(--accent); font-weight: bold; }}
        #main-content {{ flex-grow: 1; padding: 40px; overflow-y: auto; background: #fff; }}
        .content-container {{ max-width: 900px; margin: 0 auto; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        h1 {{ border-bottom: 2px solid var(--accent); padding-bottom: 10px; }}
        pre {{ background: var(--code-bg); color: #abb2bf; padding: 15px; border-radius: 6px; overflow-x: auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        code {{ font-family: 'Consolas', 'Courier New', monospace; }}
        img {{ max-width: 100%; border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: 20px 0; }}
        .mermaid {{ text-align: center; margin: 30px 0; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .mermaid-error {{ color: #D92D20; font-weight: bold; padding: 10px; border: 1px solid #D92D20; border-radius: 4px; background: #ffe6e6; }}
    </style>
</head>
<body>

    <div id="sidebar">
        <div class="sidebar-header" onclick="goHome()">PS26145 Home</div>
        <div id="module-list"></div>
    </div>

    <div id="main-content">
        <!-- Main Page Content injected by Python -->
        <div id="home-view">
            {main_page_html}
        </div>
        <!-- Module Markdown Content injected by JS -->
        <div class="content-container" id="content" style="display: none;"></div>
    </div>

    <script>
        const moduleData = {modules_json_string};
        const modulesList = {modules_list_json};

        mermaid.initialize({{ startOnLoad: false, theme: 'default', suppressErrorRendering: true }});

        const renderer = new marked.Renderer();
        const originalCodeRenderer = renderer.code.bind(renderer);
        renderer.code = function(code, language, isEscaped) {{
            if (language === 'mermaid') {{
                return '<div class="mermaid">' + code + '</div>';
            }}
            return originalCodeRenderer(code, language, isEscaped);
        }};

        marked.setOptions({{
            renderer: renderer,
            highlight: function(code, lang) {{
                if (lang && hljs.getLanguage(lang)) {{
                    return hljs.highlight(code, {{ language: lang }}).value;
                }}
                return hljs.highlightAuto(code).value;
            }}
        }});

        const sidebarElement = document.getElementById('module-list');
        const contentDiv = document.getElementById('content');
        const homeView = document.getElementById('home-view');

        // Populate sidebar
        modulesList.forEach(mod => {{
            const div = document.createElement('div');
            div.className = 'module-link';
            div.id = 'link-' + mod.id;
            div.innerText = mod.name;
            div.title = mod.name;
            div.onclick = () => loadModule(mod.id);
            sidebarElement.appendChild(div);
        }});
        
        function goHome() {{
            document.querySelectorAll('.module-link').forEach(el => el.classList.remove('active'));
            contentDiv.style.display = 'none';
            homeView.style.display = 'block';
            document.getElementById('main-content').scrollTop = 0;
        }}

        async function renderMermaidAsync() {{
            const nodes = document.querySelectorAll('.mermaid');
            if (nodes.length === 0) return;
            
            for (let i = 0; i < nodes.length; i++) {{
                const node = nodes[i];
                node.removeAttribute('data-processed');
                const id = 'mermaid-svg-' + Math.random().toString(36).substr(2, 9);
                try {{
                    const {{ svg }} = await mermaid.render(id, node.textContent);
                    node.innerHTML = svg;
                }} catch (e) {{
                    console.warn("Mermaid rendering failed for a block:", e);
                    node.innerHTML = `<div class="mermaid-error">⚠️ Mermaid Syntax Error: Could not render flowchart. Proceeding anyway.</div><pre><code>${{node.textContent}}</code></pre>`;
                }}
            }}
        }}

        function loadModule(id) {{
            document.querySelectorAll('.module-link').forEach(el => el.classList.remove('active'));
            document.getElementById('link-' + id).classList.add('active');
            
            homeView.style.display = 'none';
            contentDiv.style.display = 'block';

            if (moduleData[id]) {{
                contentDiv.innerHTML = marked.parse(moduleData[id]);
                renderMermaidAsync();
                
                if (window.MathJax) {{
                    MathJax.typesetPromise([contentDiv]).catch(err => console.warn(err));
                }}
                
                document.getElementById('main-content').scrollTop = 0;
            }} else {{
                contentDiv.innerHTML = `<h1>Error Loading Module</h1><p>Module ID ${{id}} not found in memory.</p>`;
            }}
        }}
    </script>
</body>
</html>
"""
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(html_output.strip())
    print(f"Dashboard successfully compiled at {INDEX_PATH}")

if __name__ == "__main__":
    build_dashboard()
