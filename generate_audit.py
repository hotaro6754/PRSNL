import os
import re

patterns = [r"cyberos", r"cyberos", r"cyberos", r"cyberos"]
regex = re.compile("|".join(patterns), re.IGNORECASE)

audit_lines = ["# RENAME AUDIT", "", "| OLD REFERENCE | LOCATION | TYPE | NEW REFERENCE | SAFE TO RENAME | REASON |", "|---|---|---|---|---|---|"]

ignore_dirs = [".git", "node_modules", ".next", "__pycache__", "venv", ".venv", ".pytest_cache", ".agents"]
binary_exts = [".pkl", ".jsonl", ".jpg", ".png", ".pyc", ".pack", ".idx", ".pcap"]

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    for file in files:
        if any(file.endswith(ext) for ext in binary_exts):
            continue
        path = os.path.join(root, file)
        
        # Check filename
        if regex.search(file):
            new_file = regex.sub("cyberos", file)
            safe = "YES" if "historical" not in file.lower() else "NO"
            reason = "File/dir name matches pattern"
            audit_lines.append(f"| `{file}` | `{path}` | Filename | `{new_file}` | {safe} | {reason} |")
        
        # Check content
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                matches = list(set(m.group(0) for m in regex.finditer(content)))
                if matches:
                    safe = "YES"
                    reason = "Code/Config/Text replacement"
                    if "historical" in path.lower() or "dataset" in path.lower() or "report" in path.lower():
                        safe = "REVIEW"
                        reason = "Might be historical context"
                    for match in matches:
                        new_match = "cyberos" if match.islower() else ("CYBEROS" if match.isupper() else "CyberOS")
                        audit_lines.append(f"| `{match}` | `{path}` | Content | `{new_match}` | {safe} | {reason} |")
        except Exception:
            pass

os.makedirs("artifacts", exist_ok=True)
with open("artifacts/RENAME_AUDIT.md", "w", encoding="utf-8") as f:
    f.write("\n".join(audit_lines))

print(f"Generated RENAME_AUDIT.md with {len(audit_lines) - 4} entries.")
