import os
import re

pattern = re.compile(r"sih[-_]?26145|cyberos", re.IGNORECASE)
ignore_dirs = [".git", "node_modules", ".next", "__pycache__", "venv", ".venv", ".pytest_cache", ".agents", "artifacts"]
binary_exts = [".pkl", ".jsonl", ".jpg", ".png", ".pyc", ".pack", ".idx", ".pcap", ".xml"]

def get_replacement(match):
    original = match.group(0)
    if original.islower():
        return "cyberos"
    elif original.isupper():
        if original == "CyberOS":
            return "CyberOS"
        return "CYBEROS"
    else:
        return "CyberOS"

for root, dirs, files in os.walk(".", topdown=True):
    dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
    
    for name in files:
        if any(name.endswith(ext) for ext in binary_exts): continue
        if name.endswith(".md"): continue # Skip markdown to avoid touching historical docs
        
        filepath = os.path.join(root, name)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            if pattern.search(content):
                new_content = pattern.sub(get_replacement, content)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated {filepath}")
        except Exception:
            pass
