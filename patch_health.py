"""
Patch frontend/src/app/(dashboard)/health/page.tsx to use absolute URLs for backend fetching
"""
import re

with open('frontend/src/app/(dashboard)/health/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace relative paths with absolute ones to hit FastAPI running on port 8000
content = content.replace('fetch("/api/health")', 'fetch("http://localhost:8000/health")')
content = content.replace('fetch("/api/api/stats")', 'fetch("http://localhost:8000/api/stats")')
content = content.replace('fetch("/api/api/metrics/history")', 'fetch("http://localhost:8000/api/metrics/history")')

with open('frontend/src/app/(dashboard)/health/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched health/page.tsx")
