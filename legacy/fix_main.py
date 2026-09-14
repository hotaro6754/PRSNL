import sys
with open('backend/main.py', 'r') as f:
    code = f.read()
code = code.replace('elif request.type == "qr":\\n        from backend.content.qr_analyzer import analyze_qr\\n        score, explanation, features = analyze_qr(request.content)\\n        category = "qr_analysis"\\n        source = "qr_analyzer"\\n        title_prefix = "QR"\\n        attack_chain = ["Quishing"]\\n    elif request.type == "sms":', '''elif request.type == "qr":
        from backend.content.qr_analyzer import analyze_qr
        score, explanation, features = analyze_qr(request.content)
        category = "qr_analysis"
        source = "qr_analyzer"
        title_prefix = "QR"
        attack_chain = ["Quishing"]
    elif request.type == "sms":''')
with open('backend/main.py', 'w') as f:
    f.write(code)
