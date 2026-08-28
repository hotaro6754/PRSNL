import socket
import ipaddress
from urllib.parse import urlparse
import asyncio
from typing import List

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from backend.contracts.evidence import CyberEvidence, Provenance

class SSRFViolationError(Exception):
    pass

def is_safe_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
        if getattr(ip, "ipv4_mapped", None):
            ip = ip.ipv4_mapped
            
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            return False
        if str(ip) == "169.254.169.254":
            return False
        return True
    except ValueError:
        return False


def resolve_and_check_ssrf(url: str):
    if url.startswith("data:"):
        return True
    
    parsed = urlparse(url)
    hostname = parsed.hostname

    if not hostname:
        raise SSRFViolationError("Invalid URL: missing hostname")
    
    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise SSRFViolationError(f"Could not resolve {hostname}")
        
    for res in addr_info:
        ip_addr = res[4][0]
        if not is_safe_ip(ip_addr):
            raise SSRFViolationError(f"SSRF detected: {hostname} resolved to forbidden IP {ip_addr}")
    
    return True

async def analyze_web_page(url: str) -> List[CyberEvidence]:
    resolve_and_check_ssrf(url)
    
    evidence_items = []
    
    prov = Provenance(
        source_event_id="web_analyzer",
        input_hash="unknown",
        pipeline="web_analyzer_playwright",
        model_id="none",
        model_version="1.0",
        feature_schema_version="1.0"
    )
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        async def route_interceptor(route, request):
            try:
                resolve_and_check_ssrf(request.url)
                await route.continue_()
            except SSRFViolationError:
                await route.abort()
                
        await page.route("**/*", route_interceptor)
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=8000)
            
            forms_count = await page.locator("form").count()
            password_inputs = await page.locator("input[type='password']").count()
            
            evidence_items.append(
                CyberEvidence(
                    url=url,
                    evidence_type="form_analysis",
                    details={"forms_count": forms_count, "password_inputs": password_inputs},
                    provenance=prov
                )
            )
            
            external_scripts = await page.evaluate('''() => {
                const scripts = document.querySelectorAll("script[src]");
                const urls = [];
                scripts.forEach(s => {
                    try {
                        const scriptUrl = new URL(s.src, window.location.href);
                        if (scriptUrl.origin !== window.location.origin) {
                            urls.push(s.src);
                        }
                    } catch (e) {}
                });
                return urls;
            }''')
            
            evidence_items.append(
                CyberEvidence(
                    url=url,
                    evidence_type="external_scripts",
                    details={"external_scripts": external_scripts},
                    provenance=prov
                )
            )
            
            screenshot_bytes = await page.screenshot(full_page=True)
            import base64
            b64_screenshot = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            evidence_items.append(
                CyberEvidence(
                    url=url,
                    evidence_type="screenshot",
                    details={"screenshot_base64": b64_screenshot},
                    provenance=prov
                )
            )
            
        finally:
            await browser.close()
            
    return evidence_items
