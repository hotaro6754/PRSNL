import os
import time
from playwright.sync_api import sync_playwright

ASSETS_DIR = r"E:\sih26145-prototype\ps26145-docs\docs\assets\screenshots"
os.makedirs(ASSETS_DIR, exist_ok=True)

def capture_screenshots():
    print("Starting Playwright to capture evidence screenshots...")
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            # Navigate to local dashboard
            print("Navigating to http://localhost:3000...")
            page.goto("http://localhost:3000", timeout=30000)
            
            # Wait for dashboard to load (wait for some text or just time)
            page.wait_for_timeout(5000)

            # Capture overview
            overview_path = os.path.join(ASSETS_DIR, "dashboard_overview.png")
            page.screenshot(path=overview_path, full_page=True)
            print(f"Captured: {overview_path}")
            
            # Let's see if we can capture a specific case if they exist in the DOM
            # But the overview is the most important E2E evidence
        except Exception as e:
            print(f"Error capturing local dashboard: {e}")
            print("Fallback: Attempting to capture the HTML Dossier instead...")
            # Fallback to the generated HTML dossier if React isn't up
            try:
                page.goto(f"file://E:/sih26145-prototype/presentation/PS26145_MASTER_DOSSIER.html")
                page.wait_for_timeout(2000)
                dossier_path = os.path.join(ASSETS_DIR, "html_dossier_overview.png")
                page.screenshot(path=dossier_path, full_page=False)
                print(f"Captured fallback: {dossier_path}")
            except Exception as e2:
                print(f"Fallback also failed: {e2}")

        finally:
            browser.close()

if __name__ == "__main__":
    capture_screenshots()
