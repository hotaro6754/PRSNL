content = open(r'E:\cyberos-prototype\educational_dashboard\index.html', encoding='utf-8').read()
import re
idx = content.find('11 Metrics')
idx_srcdoc = content.find('srcdoc="', idx)
end_srcdoc = content.find('"', idx_srcdoc+8)
srcdoc = content[idx_srcdoc+8:end_srcdoc]
print('srcdoc length:', len(srcdoc))
print('Starts with:', srcdoc[:50])
print('Ends with:', srcdoc[-50:])
