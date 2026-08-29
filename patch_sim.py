import re

def patch_main_simulations():
    with open('backend/main.py', 'r', encoding='utf-8') as f:
        content = f.read()

    new_simulators = """
def do_quishing():
    import requests
    requests.post("http://127.0.0.1:8000/api/scan", json={"type": "qr", "content": "https://evil-qr.phishing.com/login"})
    
def do_smishing():
    import requests
    requests.post("http://127.0.0.1:8000/api/scan", json={"type": "sms", "content": "URGENT: Your account is suspended. Click here https://smish-update.com"})
    
def do_phishing_email():
    import requests
    requests.post("http://127.0.0.1:8000/api/scan", json={"type": "email", "content": "Dear user, wire transfer of  required immediately. See attached invoice.exe"})
    
def do_unidirectional_ip():
    import socket
    # Simulate a SYN flood (uni-directional IP flows where no SYN-ACK is returned)
    # We send to a random blackholed IP that will never respond
    for _ in range(30):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.01)
                s.connect(("10.255.255.255", 80)) # Non-routable blackhole
        except Exception: pass
"""
    # Insert new simulators before do_port_scan
    if "def do_quishing" not in content:
        content = content.replace("def do_port_scan():", new_simulators + "\ndef do_port_scan():")

    # Update simulate_attack route
    sim_orig = '''    elif attack_type == "dga":
        background_tasks.add_task(do_dga)
    else:
        raise HTTPException(status_code=400, detail="Unknown attack type")'''
        
    sim_new = '''    elif attack_type == "dga":
        background_tasks.add_task(do_dga)
    elif attack_type == "qr":
        background_tasks.add_task(do_quishing)
    elif attack_type == "sms":
        background_tasks.add_task(do_smishing)
    elif attack_type == "email":
        background_tasks.add_task(do_phishing_email)
    elif attack_type == "uni_directional":
        background_tasks.add_task(do_unidirectional_ip)
    else:
        raise HTTPException(status_code=400, detail="Unknown attack type")'''
        
    content = content.replace(sim_orig, sim_new)

    with open('backend/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
patch_main_simulations()
print("Simulation logic added.")
