import re

with open('backend/content/threat_intel.py', 'r') as f:
    code = f.read()

replacement = """
from backend.content.web_analyzer import analyze_web_page, SSRFViolationError

async def check_playwright(url: str, score: float) -> list:
    evidence = []
    try:
        # 10 second timeout so we don't hang the API
        import asyncio
        import logging
        logger = logging.getLogger('ThreatIntel')
        logger.info(f"Starting Playwright Sandbox for: {url}")
        results = await asyncio.wait_for(analyze_web_page(url), timeout=10.0)
        
        # results is a List[CyberEvidence], we need to convert to dicts for our current pipeline
        for ev in results:
            evidence.append({
                "evidence_type": f"Playwright_{ev.evidence_type}",
                "details": ev.details
            })
            
    except asyncio.TimeoutError:
        logger.warning(f"Playwright Sandbox timeout for {url}")
        evidence.append({
            "evidence_type": "Playwright_Sandbox",
            "details": {"source": "Local Sandbox", "status": "DEGRADED", "reason": "Timeout exceeded (10.0s)"}
        })
    except SSRFViolationError as e:
        logger.warning(f"Playwright Sandbox SSRF Block: {e}")
        evidence.append({
            "evidence_type": "Playwright_Sandbox",
            "details": {"source": "Local Sandbox", "status": "BLOCKED", "reason": f"SSRF Protection: {e}"}
        })
    except Exception as e:
        logger.error(f"Playwright Sandbox failed: {e}")
        evidence.append({
            "evidence_type": "Playwright_Sandbox",
            "details": {"source": "Local Sandbox", "status": "FAILED", "reason": str(e)}
        })
        
    return evidence
"""

code = re.sub(r'async def check_playwright[\s\S]*?return evidence', replacement.strip(), code)

with open('backend/content/threat_intel.py', 'w') as f:
    f.write(code)
print("Updated check_playwright to use actual web_analyzer")
