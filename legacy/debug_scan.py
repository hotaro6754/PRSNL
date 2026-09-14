import asyncio
import sys

from backend.main import scan_content, ScanRequest

async def test():
    req = ScanRequest(type="url", content="http://evil.com")
    try:
        res = await scan_content(req)
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
