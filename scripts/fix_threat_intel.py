import re

with open('backend/content/threat_intel.py', 'r') as f:
    code = f.read()

replacement = """
from backend.content.web_analyzer import analyze_web_page, SSRFViolationError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

async def check_playwright(url: str, score: float) -> list:
    evidence = []
    try:
        import asyncio
        import logging
        logger = logging.getLogger('ThreatIntel')
        logger.info(f"Starting Playwright Sandbox for: {url}")
        
        # We give the entire function 12 seconds, while goto is limited to 8s inside.
        results = await asyncio.wait_for(analyze_web_page(url), timeout=12.0)
        
        for ev in results:
            evidence.append({
                "evidence_type": f"Playwright_{ev.evidence_type}",
                "details": ev.details
            })
            
    except PlaywrightTimeoutError:
        logger.warning(f"Playwright navigation timeout for {url}")
        evidence.append({
            "evidence_type": "Playwright_Sandbox",
            "details": {"source": "Local Sandbox", "status": "DEGRADED", "reason": "navigation_timeout"}
        })
    except asyncio.TimeoutError:
        logger.warning(f"Playwright overall async timeout for {url}")
        evidence.append({
            "evidence_type": "Playwright_Sandbox",
            "details": {"source": "Local Sandbox", "status": "DEGRADED", "reason": "analysis_timeout"}
        })
    except SSRFViolationError as e:
        logger.warning(f"Playwright Sandbox SSRF Block: {e}")
        evidence.append({
            "evidence_type": "Playwright_Sandbox",
            "details": {"source": "Local Sandbox", "status": "BLOCKED", "reason": str(e)}
        })
    except Exception as e:
        logger.error(f"Playwright Sandbox failed: {e}")
        evidence.append({
            "evidence_type": "Playwright_Sandbox",
            "details": {"source": "Local Sandbox", "status": "FAILED", "reason": str(e)}
        })
        
    return evidence
"""

code = re.sub(r'from backend\.content\.web_analyzer import analyze_web_page, SSRFViolationError[\s\S]*?async def check_playwright[\s\S]*?return evidence', replacement.strip(), code)

with open('backend/content/threat_intel.py', 'w') as f:
    f.write(code)
print("Updated threat_intel.py with precise exception handling")
