import traceback
def test():
    try:
        from backend.content.url_analyzer import analyze_url
        evidence_ledger = []
        is_suspicious = analyze_url("http://evil.com", evidence_ledger)
        print("Success:", is_suspicious, evidence_ledger)
    except Exception as e:
        traceback.print_exc()
if __name__ == "__main__":
    test()
