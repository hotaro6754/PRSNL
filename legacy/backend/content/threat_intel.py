import httpx
import logging

logger = logging.getLogger('ThreatIntel')

async def check_misp_urlhaus(url: str, score: float) -> list:
    evidence = []
    
    # URLHaus Real API Check
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.post('https://urlhaus-api.abuse.ch/v1/url/', data={'url': url})
            if resp.status_code == 200:
                data = resp.json()
                if data.get('query_status') == 'ok':
                    evidence.append({
                        "evidence_type": "URLHaus_Blacklist_Match",
                        "details": {
                            "source": "URLHaus API", 
                            "match": url,
                            "threat": data.get('threat', 'unknown'),
                            "tags": data.get('tags', [])
                        }
                    })
    except Exception as e:
        logger.warning(f"URLHaus lookup failed: {e}")
        evidence.append({
            "evidence_type": "URLHaus_Status",
            "details": {"source": "URLHaus API", "status": "DEGRADED", "error": str(e)}
        })
        
    return evidence

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

async def check_agent_reach(text: str, score: float) -> list:
    evidence = []
    # Agent reach is external LLM
    evidence.append({
        "evidence_type": "Agent-Reach_NLP",
        "details": {"source": "Agent-Reach", "status": "DEGRADED", "reason": "No provider API key configured"}
    })
    return evidence

class ThreatIntelProvider:
    def __init__(self):
        pass
