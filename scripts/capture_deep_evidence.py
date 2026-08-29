import os
from playwright.sync_api import sync_playwright

ASSETS_DIR = r"E:\cyberos-prototype\cyberos-docs\docs\assets\screenshots"
os.makedirs(ASSETS_DIR, exist_ok=True)

def capture():
    print("Capturing detailed E2E screenshots...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            page.goto("http://localhost:3000", timeout=30000)
            page.wait_for_timeout(5000)  # Wait for WebSocket data to populate

            # Full dashboard screenshot
            page.screenshot(path=os.path.join(ASSETS_DIR, "dashboard_full.png"), full_page=True)
            print("Captured full dashboard.")

            # Attempt to capture specific panels by locating generic UI structures
            # We will try to find elements containing specific text
            
            # Health Panel Evidence
            health_elements = page.get_by_text("Redpanda", exact=False)
            if health_elements.count() > 0:
                health_elements.first.locator("..").locator("..").screenshot(path=os.path.join(ASSETS_DIR, "health_panel.png"))
                print("Captured health panel.")

            # Threat Evidence
            threat_elements = page.get_by_text("DDoS", exact=False)
            if threat_elements.count() > 0:
                threat_elements.first.locator("..").locator("..").screenshot(path=os.path.join(ASSETS_DIR, "ddos_evidence.png"))
                print("Captured DDoS evidence.")
                
            model_elements = page.get_by_text("v5", exact=False)
            if model_elements.count() > 0:
                model_elements.first.locator("..").screenshot(path=os.path.join(ASSETS_DIR, "model_evidence.png"))
                print("Captured Model version evidence.")

        except Exception as e:
            print(f"Error during capture: {e}")

        finally:
            browser.close()

if __name__ == "__main__":
    capture()
