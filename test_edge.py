from playwright.sync_api import sync_playwright

print('Starting edge test...')
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            headless=True
        )
        page = browser.new_page()
        page.goto('https://example.com')
        page.screenshot(path='edge_test.png')
        browser.close()
        print('Edge success!')
except Exception as e:
    print('Error:', e)
