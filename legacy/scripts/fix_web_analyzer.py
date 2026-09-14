import re

with open('backend/content/web_analyzer.py', 'r') as f:
    code = f.read()

# Change networkidle to domcontentloaded and add a strict 8s timeout to goto
code = code.replace(
    'await page.goto(url, wait_until="networkidle")',
    'await page.goto(url, wait_until="domcontentloaded", timeout=8000)'
)

# Add playwright TimeoutError catching if needed, but since we want to catch the exact cause:
# Playwright throws a TimeoutError. We should import it.
if 'from playwright.async_api import async_playwright' in code:
    code = code.replace(
        'from playwright.async_api import async_playwright',
        'from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError'
    )

with open('backend/content/web_analyzer.py', 'w') as f:
    f.write(code)
print("Updated web_analyzer.py to use domcontentloaded and 8s timeout")
