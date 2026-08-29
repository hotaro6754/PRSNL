from backend.engines import analyze_content
import traceback

def test():
    try:
        raw_detections = {
            "url_analysis": {"suspicious": True, "evidence": []},
            "email_analysis": {},
            "sms_analysis": {},
            "qr_analysis": {}
        }
        res = analyze_content("url", "http://evil.com", raw_detections)
        print("Success:", res)
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    test()
