import os
import re

# Match variations of cyberos and cyberos
# We will treat CyberOS differently if it has "Problem Statement" nearby, but for now we'll do a regex replacement function.
def get_replacement(match):
    original = match.group(0)
    # If it's all lowercase
    if original.islower():
        return "cyberos"
    # If it's all uppercase
    elif original.isupper():
        # Keep CyberOS if it's strictly "CyberOS" in some contexts? The instructions say rename cyberos to CyberOS unless historical.
        # "CyberOS" -> "CYBEROS" or "CyberOS"? Usually product name is "CyberOS".
        if original == "CyberOS":
            return "CyberOS"
        return "CYBEROS"
    # Title case or mixed
    else:
        return "CyberOS"

pattern = re.compile(r"sih[-_]?26145|cyberos", re.IGNORECASE)

# Files we should absolutely NEVER touch:
ignore_files = ["RENAME_AUDIT.md", "generate_audit.py", "smart_rename.py"]
ignore_dirs = [".git", "node_modules", ".next", "__pycache__", "venv", ".venv", ".pytest_cache", ".agents", "artifacts"]
binary_exts = [".pkl", ".jsonl", ".jpg", ".png", ".pyc", ".pack", ".idx", ".pcap", ".xml"]

def is_historical_context(text, start, end):
    # check surrounding 50 chars for "historical", "origin", "evolved from", "Problem Statement"
    context = text[max(0, start-50):min(len(text), end+50)].lower()
    if "historical" in context or "evolved" in context or "problem statement" in context or "origin" in context:
        return True
    return False

renamed_files = 0
updated_files = 0

for root, dirs, files in os.walk(".", topdown=False):
    # filter dirs
    dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
    
    for name in files:
        if name in ignore_files: continue
        if any(name.endswith(ext) for ext in binary_exts): continue
        if ".agents" in root or "artifacts" in root: continue
        
        filepath = os.path.join(root, name)
        
        # 1. Update Content
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Find all matches
            matches = list(pattern.finditer(content))
            if matches:
                new_content = ""
                last_idx = 0
                changed = False
                for m in matches:
                    new_content += content[last_idx:m.start()]
                    original = m.group(0)
                    
                    # If it's a markdown file and historical context, skip it!
                    if filepath.endswith(".md") and is_historical_context(content, m.start(), m.end()):
                        new_content += original
                    else:
                        new_content += get_replacement(m)
                        changed = True
                    
                    last_idx = m.end()
                new_content += content[last_idx:]
                
                if changed:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    updated_files += 1
        except Exception as e:
            pass
            
        # 2. Rename File
        if pattern.search(name):
            new_name = pattern.sub(get_replacement, name)
            new_filepath = os.path.join(root, new_name)
            os.rename(filepath, new_filepath)
            renamed_files += 1

    # 3. Rename Dir
    for name in dirs:
        if name in ignore_dirs: continue
        if pattern.search(name):
            new_name = pattern.sub(get_replacement, name)
            os.rename(os.path.join(root, name), os.path.join(root, new_name))
            
print(f"Updated content in {updated_files} files.")
print(f"Renamed {renamed_files} files.")
