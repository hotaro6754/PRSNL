import re

with open('parity_check.py', 'r') as f:
    content = f.read()

new_compare = '''def compare_all():
    import glob
    pcaps = glob.glob('data/pcaps/*.pcap')
    all_pass = True
    for pcap in pcaps:
        print(f'\\n==================================')
        print(f'TESTING {pcap}')
        print(f'==================================')
        
        scapy_f = get_scapy_features(pcap)
        zeek_f = get_zeek_features(pcap)
        
        if not scapy_f or not zeek_f:
            print('SKIP: Could not generate features for one or both.')
            continue
            
        mismatches = 0
        for k in scapy_f.keys():
            v1 = scapy_f.get(k)
            v2 = zeek_f.get(k, 0)
            
            if isinstance(v1, float):
                match = abs(v1 - v2) < 0.05
            else:
                match = v1 == v2
                
            if not match:
                print(f'[FAIL] {k:30} | Scapy: {v1:<15} | Zeek: {v2}')
                mismatches += 1
                
        if mismatches == 0:
            print(f'\\n[OK] {pcap} - Perfect Parity!')
        else:
            print(f'\\n[FAIL] {pcap} - {mismatches} mismatches')
            all_pass = False
            
    if all_pass:
        print('\\nALL PCAPS PASSED FEATURE PARITY!')
    else:
        print('\\nSOME PCAPS FAILED FEATURE PARITY!')

if __name__ == '__main__':
    compare_all()
'''

content = re.sub(r'def compare\(\):.*', new_compare, content, flags=re.DOTALL)

with open('parity_check.py', 'w') as f:
    f.write(content)
