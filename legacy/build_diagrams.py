import os

OUTPUT_DIR = r"E:\cyberos-prototype\presentation\diagrams"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        :root {{
            --navy: #0B1F3A;
            --sih-blue: #0066B3;
            --blue-light: #EAF4FB;
            --green: #198754;
            --amber: #F4A62A;
            --red: #D92D20;
            --gray: #667085;
            --light: #F7F9FC;
            --white: #FFFFFF;
        }}
        body {{
            margin: 0; padding: 0; font-family: 'Inter', system-ui, sans-serif;
            background: #e0e0e0; display: flex; justify-content: center; align-items: center; min-height: 100vh;
        }}
        .canvas {{
            width: 1600px; height: 900px; background: var(--white); box-sizing: border-box; padding: 50px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1); position: relative; overflow: hidden;
        }}
        .toolbar {{ position: absolute; top: -40px; right: 0; }}
        .toolbar button {{ background: var(--navy); color: var(--white); border: none; padding: 5px 15px; cursor: pointer; border-radius: 4px; }}
        h1 {{ color: var(--navy); font-size: 40px; margin: 0 0 10px 0; }}
        h2 {{ color: var(--gray); font-size: 24px; margin: 0 0 40px 0; font-weight: normal; }}
        .box {{ background: var(--white); border: 2px solid var(--sih-blue); border-radius: 8px; padding: 15px; text-align: center; font-size: 18px; font-weight: 600; color: var(--navy); box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        @media print {{ body {{ background: none; }} .toolbar {{ display: none; }} .canvas {{ box-shadow: none; width: 100%; height: 100vh; page-break-after: always; padding: 20px; }} }}
    </style>
</head>
<body>
    <div style="position:relative;">
        <div class="toolbar"><button onclick="window.print()">Print / Export PDF</button></div>
        <div class="canvas">
            <h1>{title}</h1>
            <h2>{subtitle}</h2>
            <div class="content">{content}</div>
        </div>
    </div>
</body>
</html>"""

diagrams = []

# 01 Hero Solution
diagrams.append({
    "filename": "01_hero_solution.html",
    "title": "Proposed Solution: Passive Threat Detection",
    "subtitle": "Unidirectional IP Traffic Monitoring & Intelligence Pipeline",
    "content": """
    <div style="display:flex; height:600px; gap:40px; align-items:center;">
        <!-- Context -->
        <div style="flex:1; background:var(--light); border:2px solid var(--gray); border-radius:8px; height:80%; display:flex; align-items:center; justify-content:center;">
            <div style="font-size:24px; font-weight:bold; color:var(--navy);">PROTECTED NETWORK</div>
        </div>
        <div style="font-size:40px; color:var(--sih-blue);">→</div>
        <!-- Boundary -->
        <div style="flex:1.5; border:4px dashed var(--red); border-radius:8px; height:80%; position:relative; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:20px;">
            <div style="position:absolute; top:-16px; background:var(--white); padding:0 15px; color:var(--red); font-weight:bold; font-size:20px;">ONE-WAY OBSERVATION BOUNDARY</div>
            <div class="box" style="width:80%;">PASSIVE MIRROR / TAP / DATA-DIODE</div>
            <div style="font-size:30px; color:var(--sih-blue);">↓</div>
            <div class="box" style="width:80%;">MONITORING INTERFACE</div>
            <div style="font-size:30px; color:var(--sih-blue);">↓</div>
            <div class="box" style="width:80%;">ZEEK</div>
            <div style="background:var(--blue-light); padding:15px; border-radius:6px; font-weight:bold; text-align:center; color:var(--navy);">
                READ-ONLY<br>NO ACTIVE PROBING<br>NO PAYLOAD DECRYPTION
            </div>
            <div style="position:absolute; bottom:-100px; background:var(--amber); color:var(--navy); font-weight:bold; padding:15px; border-radius:6px; width:110%; text-align:center;">
                CURRENT PROTOTYPE VALIDATION: PCAP / CONTAINER<br>
                <span style="font-weight:normal;">TARGET DEPLOYMENT: PHYSICAL PASSIVE INTERFACE</span>
            </div>
        </div>
        <div style="font-size:40px; color:var(--sih-blue);">→</div>
        <!-- Enclave -->
        <div style="flex:2; background:var(--blue-light); border:2px solid var(--sih-blue); border-radius:8px; height:80%; position:relative; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:15px;">
            <div style="position:absolute; top:-16px; background:var(--white); padding:0 15px; color:var(--sih-blue); font-weight:bold; font-size:20px; border:2px solid var(--sih-blue); border-radius:4px;">INTELLIGENCE ENCLAVE</div>
            <div class="box" style="width:80%;">STREAMING INGEST</div>
            <div style="font-size:24px; color:var(--sih-blue);">↓</div>
            <div class="box" style="width:80%;">BEHAVIORAL INTELLIGENCE</div>
            <div style="font-size:24px; color:var(--sih-blue);">↓</div>
            <div class="box" style="width:80%; font-size:16px;">DETERMINISTIC + XGBOOST V5</div>
            <div style="font-size:24px; color:var(--sih-blue);">↓</div>
            <div class="box" style="width:80%;">EVIDENCE FUSION</div>
            <div style="font-size:24px; color:var(--sih-blue);">↓</div>
            <div class="box" style="width:80%; background:var(--green); color:var(--white); border-color:var(--green);">SECURITY CASE &nbsp;→&nbsp; SOC DASHBOARD</div>
        </div>
    </div>
    """
})

# 02 Problem Boundary
diagrams.append({
    "filename": "02_problem_boundary.html",
    "title": "Problem Statement",
    "subtitle": "HOW DO WE DETECT THREATS WHEN WE CAN ONLY OBSERVE?",
    "content": """
    <div style="display:flex; height:600px; padding:40px; gap:80px;">
        <div style="flex:1; display:flex; flex-direction:column; align-items:center;">
            <div class="box" style="width:100%; font-size:24px; padding:30px;">PRODUCTION NETWORK</div>
            <div style="height:120px; width:4px; background:var(--sih-blue); margin:10px 0; position:relative;">
                <div style="position:absolute; right:20px; top:40px; width:150px; font-weight:bold; font-size:20px; color:var(--sih-blue);">Observed Traffic</div>
            </div>
            <div style="width:100%; border:4px dashed var(--red); border-radius:8px; padding:40px; text-align:center; position:relative; background:var(--light);">
                <div style="position:absolute; top:-16px; left:50%; transform:translateX(-50%); background:var(--white); padding:0 15px; color:var(--red); font-weight:bold; font-size:20px; white-space:nowrap;">ONE-WAY BOUNDARY</div>
                <div style="font-size:28px; font-weight:bold; color:var(--navy);">Monitoring Enclave</div>
            </div>
            <div style="font-size:60px; color:var(--red); font-weight:bold; margin-top:20px;">X</div>
            <div style="font-size:28px; font-weight:bold; color:var(--red);">NO RETURN PATH</div>
        </div>
        <div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:40px;">
            <div style="background:var(--white); border:2px solid var(--red); border-left:12px solid var(--red); padding:30px; border-radius:8px; box-shadow:0 4px 10px rgba(0,0,0,0.05);">
                <div style="color:var(--red); font-size:24px; font-weight:bold; margin-bottom:20px;">RESTRICTIONS</div>
                <div style="font-size:22px; font-weight:bold; color:var(--navy); line-height:2;">
                    ❌ NO PROBING<br>
                    ❌ NO HANDSHAKE DEPENDENCY<br>
                    ❌ NO SOURCE CONTACT<br>
                    ❌ NO MITIGATION COMMAND
                </div>
            </div>
            <div style="background:var(--blue-light); border:2px solid var(--sih-blue); border-left:12px solid var(--sih-blue); padding:30px; border-radius:8px; box-shadow:0 4px 10px rgba(0,0,0,0.05);">
                <div style="color:var(--sih-blue); font-size:24px; font-weight:bold; margin-bottom:20px;">AVAILABLE INFORMATION</div>
                <div style="font-size:22px; font-weight:bold; color:var(--navy); line-height:2;">
                    ✅ PCAP<br>
                    ✅ NETFLOW / IPFIX / SFLOW<br>
                    ✅ DERIVED METADATA
                </div>
            </div>
        </div>
    </div>
    """
})

# 03 Technical Pipeline
diagrams.append({
    "filename": "03_technical_pipeline.html",
    "title": "Technical Pipeline",
    "subtitle": "From raw packets to prioritized security intelligence",
    "content": """
    <div style="display:flex; justify-content:space-between; margin-top:80px; padding:0 20px;">
        <!-- Stages -->
        """ + "".join([f"""
        <div style="display:flex; flex-direction:column; align-items:center; flex:1;">
            <div style="width:70px; height:70px; border-radius:50%; background:{color}; color:var(--white); font-size:28px; font-weight:bold; display:flex; align-items:center; justify-content:center; margin-bottom:20px;">{num}</div>
            <div style="font-size:22px; font-weight:bold; color:{color}; margin-bottom:20px;">{name}</div>
            <div style="background:var(--light); border:2px solid var(--gray); border-radius:8px; padding:20px; text-align:center; font-size:18px; color:var(--navy); font-weight:600; width:80%; line-height:1.6;">
                {desc}
            </div>
        </div>
        {f'<div style="font-size:40px; color:var(--sih-blue); margin-top:100px;">→</div>' if num != '06' else ''}
        """ for num, name, color, desc in [
            ('01', 'INGEST', 'var(--sih-blue)', 'Zeek<br>conn.log<br>dns.log<br>TLS metadata'),
            ('02', 'NORMALIZE', 'var(--sih-blue)', 'NetworkObservation<br>Canonical schema'),
            ('03', 'AGGREGATE', 'var(--sih-blue)', 'WindowManager<br>Host behavior'),
            ('04', 'FEATURES', 'var(--sih-blue)', 'rate / IAT<br>entropy / fan-out<br>bytes / DNS / TLS'),
            ('05', 'DETECT', 'var(--navy)', 'Rules<br>+<br>XGBoost V5'),
            ('06', 'FUSE+ALERT', 'var(--green)', 'Evidence<br>Confidence<br>SecurityCase')
        ]]) + """
    </div>
    """
})

# 04 Feature Engineering
diagrams.append({
    "filename": "04_feature_engineering.html",
    "title": "Feature Engineering Funnel",
    "subtitle": "Abstracting metadata into ML-ready behavioral signals",
    "content": """
    <div style="display:flex; flex-direction:column; align-items:center; margin-top:40px;">
        <div style="font-size:28px; font-weight:bold; color:var(--navy); margin-bottom:30px;">PASSIVE TELEMETRY</div>
        
        <div style="display:flex; width:100%; max-width:1200px; position:relative; margin-bottom:40px;">
            <div style="position:absolute; top:0; left:16.5%; width:67%; height:20px; border-top:3px solid var(--sih-blue); border-left:3px solid var(--sih-blue); border-right:3px solid var(--sih-blue);"></div>
            <div style="position:absolute; top:0; left:50%; width:3px; height:20px; background:var(--sih-blue);"></div>
            
            <div style="flex:1; display:flex; flex-direction:column; align-items:center; margin-top:20px;">
                <div class="box" style="width:70%; background:var(--navy); color:var(--white); font-size:20px;">FLOW METADATA</div>
                <div style="font-size:30px; color:var(--sih-blue); margin:10px 0;">↓</div>
                <div class="box" style="width:70%; font-size:18px; line-height:2; border-color:var(--gray);">RATE<br>BYTES<br>IAT<br>TCP STATE<br>FAN-OUT</div>
            </div>
            
            <div style="flex:1; display:flex; flex-direction:column; align-items:center; margin-top:20px;">
                <div class="box" style="width:70%; background:var(--navy); color:var(--white); font-size:20px;">DNS METADATA</div>
                <div style="font-size:30px; color:var(--sih-blue); margin:10px 0;">↓</div>
                <div class="box" style="width:70%; font-size:18px; line-height:2; border-color:var(--gray);">ENTROPY<br>QUERY LENGTH<br>N-GRAM<br>RECORD TYPE</div>
            </div>
            
            <div style="flex:1; display:flex; flex-direction:column; align-items:center; margin-top:20px;">
                <div class="box" style="width:70%; background:var(--navy); color:var(--white); font-size:20px;">TLS METADATA</div>
                <div style="font-size:30px; color:var(--sih-blue); margin:10px 0;">↓</div>
                <div class="box" style="width:70%; font-size:18px; line-height:2; border-color:var(--gray);">JA3/JA4<br>TIMING<br>PACKET SIZE<br>FLOW STATS</div>
            </div>
        </div>
        
        <div style="width:100%; max-width:1200px; position:relative; height:40px;">
            <div style="position:absolute; bottom:0; left:16.5%; width:67%; height:20px; border-bottom:3px solid var(--sih-blue); border-left:3px solid var(--sih-blue); border-right:3px solid var(--sih-blue);"></div>
            <div style="position:absolute; bottom:0; left:50%; width:3px; height:20px; background:var(--sih-blue);"></div>
        </div>
        
        <div style="font-size:30px; color:var(--sih-blue); margin:10px 0;">↓</div>
        <div class="box" style="width:400px; font-size:22px; background:var(--blue-light); border-color:var(--sih-blue);">HOST BEHAVIOUR</div>
        <div style="font-size:30px; color:var(--sih-blue); margin:10px 0;">↓</div>
        <div class="box" style="width:400px; font-size:22px; background:var(--green); color:var(--white); border-color:var(--green);">FEATURE VECTOR</div>
        
        <div style="margin-top:40px; font-size:24px; font-weight:bold; color:var(--red); padding:15px 30px; border:2px dashed var(--red); border-radius:8px;">
            BEHAVIORAL SIGNALS — NO PAYLOAD DECRYPTION
        </div>
    </div>
    """
})

# 05 Hybrid Detection
diagrams.append({
    "filename": "05_hybrid_detection.html",
    "title": "Hybrid Detection Architecture",
    "subtitle": "Combining explicit evidence with probabilistic machine learning",
    "content": """
    <div style="display:flex; flex-direction:column; align-items:center; margin-top:20px;">
        <div style="font-size:28px; font-weight:bold; color:var(--navy); margin-bottom:20px;">NETWORK EVENT</div>
        <div style="font-size:30px; color:var(--sih-blue);">↓</div>
        
        <div style="display:flex; width:100%; max-width:1000px; position:relative; margin-bottom:20px;">
            <div style="position:absolute; top:0; left:25%; width:50%; height:20px; border-top:3px solid var(--sih-blue); border-left:3px solid var(--sih-blue); border-right:3px solid var(--sih-blue);"></div>
            
            <div style="flex:1; display:flex; flex-direction:column; align-items:center; margin-top:20px;">
                <div class="box" style="width:70%; padding:30px; border-color:var(--sih-blue);">
                    <div style="font-size:24px; font-weight:bold; margin-bottom:20px; color:var(--navy);">DETERMINISTIC EVIDENCE</div>
                    <div style="text-align:left; font-size:20px; color:var(--gray); line-height:2;">
                        • FAST<br>• EXPLICIT<br>• PROTOCOL-AWARE<br>• KNOWN PATTERNS
                    </div>
                </div>
            </div>
            
            <div style="flex:1; display:flex; flex-direction:column; align-items:center; margin-top:20px;">
                <div class="box" style="width:70%; padding:30px; border-color:var(--sih-blue);">
                    <div style="font-size:24px; font-weight:bold; margin-bottom:20px; color:var(--navy);">XGBOOST V5</div>
                    <div style="text-align:left; font-size:20px; color:var(--gray); line-height:2;">
                        • BEHAVIORAL ML<br>• MULTIVARIATE<br>• GENERALIZATION<br>• ML PROBABILITY
                    </div>
                </div>
            </div>
        </div>
        
        <div style="width:100%; max-width:1000px; position:relative; height:40px;">
            <div style="position:absolute; bottom:0; left:25%; width:50%; height:20px; border-bottom:3px solid var(--sih-blue); border-left:3px solid var(--sih-blue); border-right:3px solid var(--sih-blue);"></div>
            <div style="position:absolute; bottom:0; left:50%; width:3px; height:20px; background:var(--sih-blue);"></div>
        </div>
        
        <div style="font-size:30px; color:var(--sih-blue); margin:10px 0;">↓</div>
        <div class="box" style="width:400px; font-size:24px; background:var(--navy); color:var(--white); border-color:var(--navy);">EVIDENCE FUSION</div>
        <div style="font-size:30px; color:var(--sih-blue); margin:10px 0;">↓</div>
        <div class="box" style="width:400px; font-size:24px; background:var(--green); color:var(--white); border-color:var(--green);">SECURITY CASE</div>
        
        <div style="margin-top:50px; font-size:32px; font-weight:bold; color:var(--navy); background:var(--light); padding:25px 50px; border-radius:8px; border:2px solid var(--sih-blue);">
            ML is evidence, not absolute truth.
        </div>
    </div>
    """
})

# 06 Threat Matrix
diagrams.append({
    "filename": "06_threat_matrix.html",
    "title": "Threat Coverage Matrix",
    "subtitle": "Detecting the six required CyberOS threat families + Slow HTTP entirely passively",
    "content": """
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; margin-top: 60px;">
        """ + "".join([f"""
        <div style="background:var(--white); border:2px solid var(--gray); border-radius:8px; padding:30px; box-shadow:0 4px 10px rgba(0,0,0,0.05);">
            <div style="font-size:28px; font-weight:bold; color:var(--red); margin-bottom:20px; border-bottom:2px solid var(--light); padding-bottom:15px;">{title}</div>
            <div style="font-size:20px; color:var(--navy); font-weight:600; line-height:2;">{items}</div>
        </div>
        """ for title, items in [
            ('DDoS', 'Rate &bull; SYN/UDP &bull; Source entropy'),
            ('C2 Beaconing', 'Periodicity &bull; IAT &bull; Destinations'),
            ('DGA / DNS Tunnel', 'Entropy &bull; Length &bull; N-gram'),
            ('Encrypted Sessions', 'JA3/JA4 &bull; Timing &bull; Packet size'),
            ('Reconnaissance', 'Fan-out &bull; Ports &bull; Hosts'),
            ('Data Exfiltration', 'Byte asymmetry &bull; Outbound ratio')
        ]]) + """
    </div>
    <div style="display:flex; justify-content:center; margin-top:40px;">
        <div style="width:30%; background:var(--light); border:2px solid var(--gray); border-radius:8px; padding:25px; box-shadow:0 4px 10px rgba(0,0,0,0.05);">
            <div style="font-size:24px; font-weight:bold; color:var(--red); margin-bottom:15px; border-bottom:2px solid #e0e0e0; padding-bottom:10px;">+ Slow HTTP</div>
            <div style="font-size:18px; color:var(--navy); font-weight:600; line-height:2;">Concurrency &bull; Trickle &bull; Incomplete</div>
        </div>
    </div>
    """
})

# 07 Infrastructure Architecture
diagrams.append({
    "filename": "07_infrastructure_architecture.html",
    "title": "Enterprise Infrastructure Architecture",
    "subtitle": "Decoupled, high-throughput pipeline design",
    "content": """
    <div style="display:flex; flex-direction:column; gap:60px; margin-top:60px; width:100%; max-width:1400px; margin-left:auto; margin-right:auto;">

        <div style="background:var(--blue-light); border:2px solid var(--sih-blue); border-left:20px solid var(--sih-blue); border-radius:8px; padding:40px; position:relative;">
            <div style="position:absolute; top:-18px; left:40px; background:var(--sih-blue); color:var(--white); padding:8px 20px; font-weight:bold; font-size:20px; border-radius:4px;">DATA PLANE</div>
            <div style="display:flex; justify-content:space-around; align-items:center; margin-top:10px;">
                <div class="box" style="flex:1; max-width:250px;">ZEEK</div>
                <div style="font-size:30px; color:var(--sih-blue);">→</div>
                <div class="box" style="flex:1; max-width:250px;">ZEEK ADAPTER</div>
                <div style="font-size:30px; color:var(--sih-blue);">→</div>
                <div class="box" style="flex:1; max-width:250px; background:var(--sih-blue); color:var(--white);">REDPANDA</div>
            </div>
        </div>

        <div style="background:rgba(25, 135, 84, 0.1); border:2px solid var(--green); border-left:20px solid var(--green); border-radius:8px; padding:40px; position:relative;">
            <div style="position:absolute; top:-18px; left:40px; background:var(--green); color:var(--white); padding:8px 20px; font-weight:bold; font-size:20px; border-radius:4px;">INTELLIGENCE PLANE</div>
            <div style="display:flex; justify-content:space-around; align-items:center; margin-top:10px;">
                <div class="box" style="flex:1; max-width:180px;">REDIS</div>
                <div style="font-size:30px; color:var(--green);">→</div>
                <div class="box" style="flex:1; max-width:180px;">WINDOW MANAGER</div>
                <div style="font-size:30px; color:var(--green);">→</div>
                <div class="box" style="flex:1; max-width:180px;">FEATURE ENGINE</div>
                <div style="font-size:30px; color:var(--green);">→</div>
                <div class="box" style="flex:1; max-width:180px;">RULES + XGBOOST</div>
                <div style="font-size:30px; color:var(--green);">→</div>
                <div class="box" style="flex:1; max-width:180px; background:var(--green); color:var(--white);">FUSION</div>
            </div>
        </div>

        <div style="background:#E8EBF0; border:2px solid var(--navy); border-left:20px solid var(--navy); border-radius:8px; padding:40px; position:relative;">
            <div style="position:absolute; top:-18px; left:40px; background:var(--navy); color:var(--white); padding:8px 20px; font-weight:bold; font-size:20px; border-radius:4px;">SOC PLANE</div>
            <div style="display:flex; justify-content:space-around; align-items:center; margin-top:10px;">
                <div class="box" style="flex:1; max-width:250px;">MONGODB</div>
                <div style="font-size:30px; color:var(--navy);">→</div>
                <div class="box" style="flex:1; max-width:250px;">FASTAPI</div>
                <div style="font-size:30px; color:var(--navy);">→</div>
                <div class="box" style="flex:1; max-width:250px;">WEBSOCKET</div>
                <div style="font-size:30px; color:var(--navy);">→</div>
                <div class="box" style="flex:1; max-width:250px; background:var(--navy); color:var(--white);">NEXT.JS SOC</div>
            </div>
        </div>

    </div>
    """
})

# 08 Failure Recovery
diagrams.append({
    "filename": "08_failure_recovery.html",
    "title": "Failure & Recovery Constraints",
    "subtitle": "Ensuring resilience against component degradation",
    "content": """
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 40px; margin-top: 80px;">
        """ + "".join([f"""
        <div style="background:var(--white); border:1px solid var(--gray); border-radius:8px; padding:30px; text-align:center; box-shadow:0 4px 10px rgba(0,0,0,0.05);">
            <div style="font-size:22px; font-weight:bold; color:var(--navy); margin-bottom:30px;">{title}</div>
            <div style="font-size:18px; font-weight:bold; color:var(--red);">{s1}</div>
            <div style="font-size:30px; color:var(--sih-blue); margin:15px 0;">↓</div>
            <div style="font-size:18px; font-weight:bold; color:var(--amber);">{s2}</div>
            <div style="font-size:30px; color:var(--sih-blue); margin:15px 0;">↓</div>
            <div style="font-size:18px; font-weight:bold; color:var(--gray);">{s3}</div>
            <div style="font-size:30px; color:var(--sih-blue); margin:15px 0;">↓</div>
            <div style="font-size:18px; font-weight:bold; color:var(--green);">{s4}</div>
        </div>
        """ for title, s1, s2, s3, s4 in [
            ('ZEEK FAILURE', 'ZEEK DOWN', 'HEALTH DEGRADED', 'ADAPTER RECOVERY', 'STREAM RESUMES'),
            ('REDPANDA FAILURE', 'BROKER DOWN', 'RETRY / BUFFER', 'BROKER RECOVERS', 'CONSUMERS RESUME'),
            ('ML FAILURE', 'ML WORKER DOWN', 'RULE ENGINE CONTINUES', 'ML QUEUES', 'ML RECOVERS'),
            ('MONGODB FAILURE', 'DATABASE DOWN', 'DEGRADED STATE', 'DURABLE BUFFER', 'DATABASE RECOVERY')
        ]]) + """
    </div>
    <div style="margin-top:70px; text-align:center; font-size:28px; font-weight:bold; color:var(--navy); background:var(--blue-light); padding:25px; border-radius:8px;">
        Restart-resilient, at-least-once semantics.
    </div>
    """
})

# 09 Impact Before After
diagrams.append({
    "filename": "09_impact_before_after.html",
    "title": "Impact / Benefits",
    "subtitle": "Securing one-way infrastructure",
    "content": """
    <div style="display:flex; gap:80px; margin-top:60px; height:500px;">
        <!-- BEFORE -->
        <div style="flex:1; background:#FEF3F2; border:2px solid var(--red); border-radius:8px; padding:40px; display:flex; flex-direction:column; align-items:center;">
            <div style="font-size:28px; font-weight:bold; color:var(--red); margin-bottom:40px;">BEFORE</div>
            <div class="box arrow-down" style="width:70%; border-color:var(--red);">ONE-WAY TRAFFIC</div>
            <div class="box arrow-down" style="width:70%; border-color:var(--red);">RAW OBSERVATIONS</div>
            <div class="box arrow-down" style="width:70%; border-color:var(--red);">MANUAL ANALYSIS</div>
            <div class="box arrow-down" style="width:70%; border-color:var(--red);">DELAYED RESPONSE</div>
            <div class="box" style="width:70%; background:var(--red); color:var(--white); border-color:var(--red);">HIGH ANALYST LOAD</div>
        </div>
        <!-- AFTER -->
        <div style="flex:1; background:#F0FDF4; border:2px solid var(--green); border-radius:8px; padding:40px; display:flex; flex-direction:column; align-items:center;">
            <div style="font-size:28px; font-weight:bold; color:var(--green); margin-bottom:40px;">WITH PLATFORM</div>
            <div class="box arrow-down" style="width:70%; border-color:var(--green);">ONE-WAY TRAFFIC</div>
            <div class="box arrow-down" style="width:70%; border-color:var(--green);">PASSIVE TELEMETRY</div>
            <div class="box arrow-down" style="width:70%; border-color:var(--green);">BEHAVIORAL INTELLIGENCE</div>
            <div class="box arrow-down" style="width:70%; border-color:var(--green);">ML + RULES &rarr; EVIDENCE</div>
            <div class="box" style="width:70%; background:var(--green); color:var(--white); border-color:var(--green);">PRIORITIZED SECURITY CASE</div>
        </div>
    </div>
    <div style="margin-top:60px; text-align:center; font-size:30px; font-weight:bold; color:var(--navy); background:var(--light); padding:30px; border-radius:8px; border:2px solid var(--sih-blue);">
        "Turn a one-way security constraint into an intelligence advantage."
    </div>
    """
})

# 10 Research Map
diagrams.append({
    "filename": "10_research_map.html",
    "title": "Research & Ecosystem",
    "subtitle": "Standing on the shoulders of the cybersecurity open-source community",
    "content": """
    <div style="position:relative; width:1200px; height:650px; margin:40px auto 0 auto;">
        <!-- SVGs for connections -->
        <svg style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:1;" pointer-events="none">
            <line x1="600" y1="325" x2="300" y2="150" stroke="#0066B3" stroke-width="2" />
            <line x1="600" y1="325" x2="600" y2="100" stroke="#0066B3" stroke-width="2" />
            <line x1="600" y1="325" x2="900" y2="150" stroke="#0066B3" stroke-width="2" />
            <line x1="600" y1="325" x2="1000" y2="325" stroke="#0066B3" stroke-width="2" />
            <line x1="600" y1="325" x2="900" y2="500" stroke="#0066B3" stroke-width="2" />
            <line x1="600" y1="325" x2="600" y2="550" stroke="#0066B3" stroke-width="2" />
            <line x1="600" y1="325" x2="300" y2="500" stroke="#0066B3" stroke-width="2" />
            <line x1="600" y1="325" x2="200" y2="325" stroke="#0066B3" stroke-width="2" />
        </svg>
        
        <!-- Center -->
        <div style="position:absolute; top:250px; left:480px; width:240px; height:150px; background:var(--navy); color:var(--white); border-radius:75px; display:flex; flex-direction:column; justify-content:center; align-items:center; z-index:2; box-shadow:0 4px 15px rgba(0,0,0,0.2);">
            <div style="font-weight:bold; font-size:32px;">CyberOS</div>
            <div style="font-size:20px; font-weight:normal; color:#EAF4FB; margin-top:5px;">PASSIVE NDR</div>
        </div>
        
        <!-- Nodes -->
        """ + "".join([f"""
        <div style="position:absolute; top:{y}px; left:{x}px; width:260px; background:var(--white); border:2px solid var(--sih-blue); border-radius:8px; padding:20px; text-align:center; z-index:2; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
            <div style="font-weight:bold; color:var(--navy); font-size:22px;">{title}</div>
            <div style="font-size:16px; color:var(--gray); margin-top:10px; font-weight:600;">{sub}</div>
        </div>
        """ for x, y, title, sub in [
            (150, 100, 'ZEEK', 'NETWORK TELEMETRY'),
            (470, 20, 'CICIDS2017', 'INTRUSION DATA'),
            (790, 100, 'UNSW-NB15', 'CROSS-DOMAIN VALIDATION'),
            (890, 280, 'XGBOOST', 'ML CLASSIFICATION'),
            (790, 470, 'DNS / DGA', 'RESEARCH'),
            (470, 520, 'C2 BEACON', 'RESEARCH'),
            (150, 470, 'ENCRYPTED TRAFFIC', 'METADATA RESEARCH'),
            (50, 280, 'REDPANDA', 'STREAMING')
        ]]) + """
    </div>
    """
})

# 11 Metrics
diagrams.append({
    "filename": "11_metrics.html",
    "title": "Validation Metrics",
    "subtitle": "Objective measurements from evaluation and regression",
    "content": """
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 40px; margin-top: 80px;">
        """ + "".join([f"""
        <div style="background:var(--white); border:2px solid var(--sih-blue); border-radius:12px; padding:50px 20px; text-align:center; box-shadow:0 6px 15px rgba(0,0,0,0.05);">
            <div style="font-size:72px; font-weight:bold; color:var(--navy); margin-bottom:15px;">{val}</div>
            <div style="font-size:22px; color:var(--gray); font-weight:bold;">{lbl}</div>
        </div>
        """ for val, lbl in [
            ('98.69%', 'PRECISION'),
            ('100%', 'HELD-OUT RECALL'),
            ('99.34%', 'F1 SCORE'),
            ('0%', 'FALSE POSITIVE')
        ]]) + """
    </div>
    <div style="margin-top:80px; text-align:center; font-size:36px; font-weight:bold; color:var(--navy); background:var(--light); padding:35px; border-radius:8px; border:1px solid var(--gray);">
        11 TP &nbsp;|&nbsp; 3 TN &nbsp;|&nbsp; 0 FP &nbsp;|&nbsp; <span style="color:var(--amber);">1 FN</span>
        <div style="font-size:22px; color:var(--gray); font-weight:normal; margin-top:20px;">15-scenario regression corpus</div>
    </div>
    <div style="margin-top:40px; text-align:center; font-size:22px; color:var(--gray); font-weight:600;">
        HELD-OUT / CONTROLLED EVALUATION<br>
        <span style="display:inline-block; margin-top:15px; font-weight:normal;">~1.40 ms ML P50 &nbsp;&bull;&nbsp; ~3,120 flow records/sec &mdash; containerized buffered-ingestion benchmark</span>
    </div>
    """
})

for d in diagrams:
    html = TEMPLATE.format(title=d['title'], subtitle=d['subtitle'], content=d['content'])
    with open(os.path.join(OUTPUT_DIR, d['filename']), "w", encoding="utf-8") as f:
        f.write(html)

# Index
index_html = """<!DOCTYPE html>
<html><head><title>CyberOS Diagrams</title>
<style>
    body { font-family: sans-serif; background: #f0f2f5; padding: 40px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
    .card { background: white; padding: 20px; border-radius: 8px; text-decoration: none; color: #0B1F3A; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: block; border: 1px solid #e0e0e0; }
    .card:hover { border-color: #0066B3; }
</style></head>
<body><h1>CyberOS - SIH Internal Round Visual System</h1>
<div class="grid">
""" + "".join([f'<a class="card" href="{d["filename"]}"><strong>{d["filename"][:2]}</strong> {d["title"]}</a>' for d in diagrams]) + """
</div></body></html>"""

with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print("Generated successfully!")
