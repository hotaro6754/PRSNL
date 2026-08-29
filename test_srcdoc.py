import html
with open(r'E:\sih26145-prototype\presentation\diagrams\03_technical_pipeline.html', 'r', encoding='utf-8') as f:
    raw = f.read()
escaped = html.escape(raw)
with open('test.html', 'w', encoding='utf-8') as f:
    f.write(f'<!DOCTYPE html><html><body><iframe srcdoc="{escaped}" width="1600" height="900"></iframe></body></html>')
