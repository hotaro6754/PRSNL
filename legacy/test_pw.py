from playwright.sync_api import sync_playwright
import os
import sys

print('Starting playwright...')
try:
    with sync_playwright() as p:
        print('Launching browser...')
        browser = p.chromium.launch(headless=True)
        print('Browser launched.')
        page = browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 900})
        html_path = r'E:\cyberos-prototype\presentation\diagrams\01_hero_solution.html'
        uri = 'file:///' + html_path.replace('\\\\', '/')
        print('Navigating to', uri)
        page.goto(uri)
        print('Navigated. Taking screenshot...')
        page.screenshot(path='test_hero.png', full_page=True)
        browser.close()
        print('Success!')
except Exception as e:
    print('Error:', e)
