import os

out_dir = r"E:\cyberos-prototype\educational_dashboard\raw_modules"
os.makedirs(out_dir, exist_ok=True)

modules = {
    "021": r"""# Module 21: Firewalls (The Perimeter)
## 1. What is it? (Explain from scratch for a complete beginner)
A firewall is like a security guard at the entrance of a building. It sits between your computer network (or a single computer) and the internet, checking all the digital traffic trying to come in or go out. If the traffic follows the rules (like having the right ID badge), the firewall lets it through. If it doesn't, the firewall blocks it. This prevents hackers, viruses, and malicious data from entering your system.

## 2. System Architecture
```mermaid
flowchart LR
    Internet((Internet)) -->|Incoming Traffic| FW[Firewall]
    FW -->|Allowed Traffic| InternalNetwork[Internal Network]
    FW -->|Blocked Traffic| Drop[Discarded]
    InternalNetwork -->|Outgoing Traffic| FW
```

## 3. Implementation
Here is a simple example of how you might use Python (using `iptc` library) to add a firewall rule in Linux to block an IP address, or conceptually how rules are defined:

```python
# Conceptual Python representation of adding a firewall rule
class SimpleFirewall:
    def __init__(self):
        self.block_list = []

    def add_rule(self, ip_address):
        self.block_list.append(ip_address)
        print(f"Rule added: Block all traffic from {ip_address}")

    def inspect_traffic(self, source_ip):
        if source_ip in self.block_list:
            return "Blocked"
        return "Allowed"

fw = SimpleFirewall()
fw.add_rule("192.168.1.100")
print(fw.inspect_traffic("192.168.1.100")) # Blocked
print(fw.inspect_traffic("10.0.0.5"))      # Allowed
```

## 4. Line-by-Line Explanation
1. `class SimpleFirewall:`: Creates a blueprint for our simulated firewall.
2. `def __init__(self): self.block_list = []`: Initializes the firewall with an empty list of blocked IPs.
3. `def add_rule(self, ip_address):`: Defines a method to add a new rule.
4. `self.block_list.append(ip_address)`: Adds the specified IP to the block list.
5. `print(...)`: Confirms the rule was added.
6. `def inspect_traffic(self, source_ip):`: Method to check incoming traffic.
7. `if source_ip in self.block_list:`: Checks if the incoming IP is in our banned list.
8. `return "Blocked"`: If it is, reject the traffic.
9. `return "Allowed"`: If not, let the traffic through.

## 5. Summary
Firewalls are the first line of defense in network security. They act as a barrier between your internal network and the wild internet, filtering traffic based on predefined rules to keep unauthorized or malicious traffic out while letting legitimate communication happen.
""",
    "022": r"""# Module 22: IDS and IPS (Intrusion Detection/Prevention)
## 1. What is it? (Explain from scratch for a complete beginner)
If a firewall is the security guard at the door, an **Intrusion Detection System (IDS)** is the security camera inside the building. It watches network traffic and alerts you if it sees anything suspicious (like a break-in attempt). An **Intrusion Prevention System (IPS)** takes it a step further: it's a security camera equipped with automated traps. When the IPS sees an attack, it doesn't just alert you; it actively blocks the attack from happening.

## 2. System Architecture
```mermaid
flowchart TD
    Traffic[Network Traffic] --> IDS[Intrusion Detection System]
    Traffic --> IPS[Intrusion Prevention System]
    IDS -->|Analyzes & Alerts| Admin[Security Admin]
    IPS -->|Analyzes & Blocks| Drop[Drop Malicious Packets]
    IPS -->|Allows| Network[Internal Network]
```

## 3. Implementation
Here is a conceptual Python example showing the difference between IDS and IPS logic:

```python
class SecuritySystem:
    def __init__(self, mode):
        self.mode = mode # 'IDS' or 'IPS'
        self.signatures = ["sql_injection", "malware_signature_xyz"]

    def analyze_packet(self, packet_content):
        for sig in self.signatures:
            if sig in packet_content:
                if self.mode == 'IDS':
                    return "ALERT: Malicious traffic detected!"
                elif self.mode == 'IPS':
                    return "BLOCKED: Malicious traffic stopped!"
        return "Allowed"

ids = SecuritySystem('IDS')
print("IDS:", ids.analyze_packet("normal_web_request"))
print("IDS:", ids.analyze_packet("some_text_with_sql_injection"))

ips = SecuritySystem('IPS')
print("IPS:", ips.analyze_packet("some_text_with_sql_injection"))
```

## 4. Line-by-Line Explanation
1. `class SecuritySystem:`: Blueprint for our IDS/IPS.
2. `def __init__(self, mode):`: Sets up the system to act as either an IDS or IPS.
3. `self.signatures = [...]`: A list of known bad patterns (signatures) to look for.
4. `def analyze_packet(self, packet_content):`: Takes a chunk of network data (packet) to inspect.
5. `for sig in self.signatures:`: Loops through known threats.
6. `if sig in packet_content:`: Checks if the threat pattern is in the packet.
7. `if self.mode == 'IDS': return "ALERT..."`: If it's an IDS, it just warns us.
8. `elif self.mode == 'IPS': return "BLOCKED..."`: If it's an IPS, it actively blocks the data.
9. `return "Allowed"`: If no threats match, traffic passes safely.

## 5. Summary
An IDS monitors and alerts on potential attacks but doesn't stop them, whereas an IPS monitors, alerts, and actively takes action to block the threats. Together with firewalls, they provide deep layered security for networks.
""",
    "023": r"""# Module 23: SIEM (Security Information and Event Management)
## 1. What is it? (Explain from scratch for a complete beginner)
Imagine a massive factory with thousands of sensors, alarms, and cameras. It would be impossible for one person to watch them all individually. A **SIEM (Security Information and Event Management)** system is like the central control room. It collects logs (records of events) from firewalls, computers, IDS/IPS, and servers, puts them all in one place, and analyzes them to find hidden patterns. If someone logs in from New York and China at the exact same time, the SIEM connects the dots and sounds a unified alarm.

## 2. System Architecture
```mermaid
flowchart TD
    FW[Firewall Logs] --> SIEM[(SIEM Engine)]
    Server[Server Logs] --> SIEM
    AV[Antivirus Logs] --> SIEM
    SIEM -->|Correlation| Dashboard[Security Dashboard]
    SIEM -->|Alerts| Analyst[SOC Analyst]
```

## 3. Implementation
Here is a Python script demonstrating how a SIEM correlates events to detect a "Brute Force" attack (multiple failed logins followed by a success):

```python
from collections import defaultdict
import time

class MiniSIEM:
    def __init__(self):
        self.failed_logins = defaultdict(int)

    def process_log(self, user, action):
        if action == "LOGIN_FAILED":
            self.failed_logins[user] += 1
            if self.failed_logins[user] > 3:
                print(f"SIEM ALERT: Possible Brute Force Attack on {user}!")
        elif action == "LOGIN_SUCCESS":
            if self.failed_logins[user] > 3:
                print(f"CRITICAL SIEM ALERT: Compromised account {user} (Brute Force Succeeded)!")
            self.failed_logins[user] = 0 # Reset on success

siem = MiniSIEM()
siem.process_log("admin", "LOGIN_FAILED")
siem.process_log("admin", "LOGIN_FAILED")
siem.process_log("admin", "LOGIN_FAILED")
siem.process_log("admin", "LOGIN_FAILED") # Triggers alert
siem.process_log("admin", "LOGIN_SUCCESS") # Triggers critical alert
```

## 4. Line-by-Line Explanation
1. `from collections import defaultdict`: Imports a helpful dictionary to count things.
2. `class MiniSIEM:`: Creates our SIEM class.
3. `self.failed_logins = defaultdict(int)`: Keeps track of how many times each user fails to log in.
4. `def process_log(self, user, action):`: Simulates receiving a log entry.
5. `if action == "LOGIN_FAILED":`: If the log says the login failed...
6. `self.failed_logins[user] += 1`: Increase the fail count for that user by 1.
7. `if self.failed_logins[user] > 3:`: If they failed more than 3 times...
8. `print(...)`: Generate a warning alert.
9. `elif action == "LOGIN_SUCCESS":`: If they finally log in...
10. `if self.failed_logins[user] > 3:`: And they previously failed many times, this means the hacker guessed the password!
11. `print(...)`: Generate a CRITICAL alert.
12. `self.failed_logins[user] = 0`: Reset the counter.

## 5. Summary
A SIEM aggregates data from across the entire IT environment and correlates it to detect complex attacks that a single security device (like a firewall) would miss. It is the central nervous system of a cybersecurity operation.
""",
    "024": r"""# Module 24: Passive vs Active Defense
## 1. What is it? (Explain from scratch for a complete beginner)
In cybersecurity, **Passive Defense** is like building a strong castle: thick walls (firewalls), strong locks (passwords), and security cameras (IDS). You wait for the enemy to attack and hope your defenses hold. **Active Defense** is sending out scouts, setting booby traps, and actively hunting for threats. Instead of just waiting, you try to confuse the attackers, waste their time (using honeypots), or actively trace where they are coming from.

## 2. System Architecture
```mermaid
flowchart LR
    Attacker((Hacker)) -->|Attacks| Network
    
    subgraph Passive Defense
        Network --> Firewall[Firewall]
        Network --> Patching[Patching/Updates]
    end
    
    subgraph Active Defense
        Network --> Honeypot[Honeypot / Decoy]
        Network --> ThreatHunt[Threat Hunting]
    end
```

## 3. Implementation
Here is a Python example of a simple Active Defense technique called a "Honeypot" (a fake service meant to trap hackers):

```python
import socket

def simple_honeypot():
    # Bind to port 22 (SSH - a common target for hackers)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 2222)) # Using 2222 for testing so we don't need root
    s.listen(5)
    print("Honeypot active. Listening for attackers...")
    
    try:
        while True:
            client_socket, address = s.accept()
            print(f"ACTIVE DEFENSE ALERT: Connection from attacker at {address}")
            # Send fake SSH banner to fool the attacker
            client_socket.send(b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.1\r\n")
            client_socket.close()
    except KeyboardInterrupt:
        print("Honeypot shut down.")

# simple_honeypot() # Uncomment to run (will block execution)
print("Honeypot script ready to deploy.")
```

## 4. Line-by-Line Explanation
1. `import socket`: Imports the library needed for network communication.
2. `def simple_honeypot():`: Defines our active defense trap.
3. `s = socket.socket(...)`: Creates a network socket.
4. `s.bind(('0.0.0.0', 2222))`: Opens port 2222 on the machine to listen for connections.
5. `s.listen(5)`: Starts listening.
6. `client_socket, address = s.accept()`: When an attacker connects, it grabs their IP address.
7. `print(...)`: Logs the attacker's IP.
8. `client_socket.send(...)`: Sends a fake server banner to make the hacker think they found a real server, wasting their time.
9. `client_socket.close()`: Disconnects them abruptly.

## 5. Summary
Passive defense focuses on hardening the environment and preventing breaches, while active defense involves proactively engaging with, deceiving, or hunting the attackers to disrupt their operations and gather intelligence.
""",
    "025": r"""# Module 25: The SOC (Security Operations Center)
## 1. What is it? (Explain from scratch for a complete beginner)
A **Security Operations Center (SOC)** is a physical or virtual room filled with cybersecurity professionals working 24/7. Think of it like a military command center or a 911 dispatch center, but for computer networks. The SOC team constantly monitors the network, uses tools like SIEMs, investigates alerts, and responds to cyber incidents in real-time to stop hackers before they steal data.

## 2. System Architecture
```mermaid
flowchart TD
    Data[Network Data / Logs] --> SIEM[SIEM System]
    SIEM --> Alerts[Security Alerts]
    Alerts --> Tier1[Tier 1 Analyst: Triage]
    Tier1 -->|Escalates| Tier2[Tier 2 Analyst: Deep Investigation]
    Tier2 -->|Escalates| Tier3[Tier 3 Analyst: Threat Hunting / Malware Eval]
    Tier1 -->|False Alarm| Close[Close Ticket]
```

## 3. Implementation
A SOC uses ticket management. Here is a Python script simulating how a SOC Analyst might triage an alert:

```python
class SOCTicket:
    def __init__(self, alert_id, severity, description):
        self.alert_id = alert_id
        self.severity = severity
        self.description = description
        self.status = "Open"

def triage_alert(ticket):
    print(f"Investigating Ticket {ticket.alert_id}: {ticket.description}")
    
    if ticket.severity == "Low":
        print("Action: False positive confirmed. Closing ticket.")
        ticket.status = "Closed"
    elif ticket.severity == "High":
        print("Action: True positive confirmed! Escalating to Incident Response (Tier 2).")
        ticket.status = "Escalated"
    
    print(f"Ticket Status: {ticket.status}\n")

# Simulate SOC alerts arriving
alert1 = SOCTicket(101, "Low", "Failed login from known employee IP.")
alert2 = SOCTicket(102, "High", "Ransomware encryption detected on Server DB-01!")

triage_alert(alert1)
triage_alert(alert2)
```

## 4. Line-by-Line Explanation
1. `class SOCTicket:`: Defines a tracking ticket for a security alert.
2. `def __init__(...)`: Assigns an ID, severity, description, and sets status to "Open".
3. `def triage_alert(ticket):`: A function representing the Tier 1 analyst's job.
4. `if ticket.severity == "Low":`: If the alert is minor...
5. `ticket.status = "Closed"`: Mark it as a false alarm or resolved.
6. `elif ticket.severity == "High":`: If the alert is critical...
7. `ticket.status = "Escalated"`: Pass the ticket up to the senior analysts for immediate action.
8. The final lines create two simulated alerts and pass them through the triage process.

## 5. Summary
The SOC is the human element of cybersecurity. While firewalls and antiviruses automate defense, the SOC is the team of experts that monitor the tools, investigate complex threats, and orchestrate the response when a breach actually happens.
""",
    "026": r"""# Module 26: Zeek Network Security Monitor (Architecture)
## 1. What is it? (Explain from scratch for a complete beginner)
**Zeek** (formerly known as Bro) is a powerful, open-source network analysis framework. Unlike a firewall that blocks traffic, or an IDS that only looks for signatures of attacks, Zeek is like a network "flight data recorder." It quietly watches all network traffic and generates highly detailed, structured logs (like spreadsheets) of exactly who talked to whom, what files were downloaded, and what protocols were used. It allows security analysts to look back in time to see exactly what happened during a hack.

## 2. System Architecture
```mermaid
flowchart TD
    Network[Raw Network Traffic] --> ZeekSensor[Zeek Sensor Engine]
    ZeekSensor -->|Event Engine| ZeekScripts[Zeek Scripting Language]
    ZeekScripts --> ConnLog[conn.log (Connections)]
    ZeekScripts --> DnsLog[dns.log (DNS Queries)]
    ZeekScripts --> HttpLog[http.log (Web Traffic)]
```

## 3. Implementation
Zeek uses its own scripting language. Here is an example of a Zeek script that prints a message to the console every time someone connects to an SSH server (Port 22):

```zeek
# Zeek Script (save as ssh_monitor.zeek)
event connection_established(c: connection)
    {
    # Check if the destination port is 22 (SSH)
    if ( c$id$resp_p == 22/tcp )
        {
        print fmt("SSH Connection Detected! Source: %s -> Destination: %s", c$id$orig_h, c$id$resp_h);
        }
    }
```
*Note: This is Zeek script syntax, not Python.*

## 4. Line-by-Line Explanation
1. `# Zeek Script`: A comment.
2. `event connection_established(c: connection)`: This is an event handler. Zeek triggers this block of code every time a network connection is successfully established. The `c` variable holds all the data about the connection.
3. `if ( c$id$resp_p == 22/tcp )`: `c$id` contains the connection IDs. `resp_p` stands for Responder Port (the destination port). We check if it is port 22 (SSH) over TCP.
4. `print fmt(...)`: The format print command.
5. `c$id$orig_h`: The Originator Host (Source IP address).
6. `c$id$resp_h`: The Responder Host (Destination IP address).
7. If someone connects via SSH, Zeek instantly prints their IP and the server's IP.

## 5. Summary
Zeek is a passive network monitor that translates complex network packets into easily readable, highly detailed logs. Its powerful scripting language allows analysts to customize exactly what data they want to extract, making it an essential tool for threat hunting and incident response.
""",
    "027": r"""# Module 27: Taps and SPAN Ports (Hardware)
## 1. What is it? (Explain from scratch for a complete beginner)
To monitor a network (using an IDS or Zeek), you need to actually *see* the traffic. Because modern networks use switches (which only send traffic to the specific computer it's meant for), you can't just plug in and see everything. 
You have two ways to get a copy of the traffic:
1. **SPAN Port (Port Mirroring):** You tell the network switch to copy all traffic from port 1 and send the copy out of port 2 (where your monitor is plugged in).
2. **Network TAP:** A physical piece of hardware you plug the cables into. It physically splits the light or electrical signal and sends a perfect, unalterable copy to your monitor.

## 2. System Architecture
```mermaid
flowchart LR
    subgraph SPAN Port
        Switch[Network Switch] -->|Normal Traffic| PC[User PC]
        Switch -.->|Copied Traffic| Monitor1[Security Monitor]
    end
    
    subgraph Network TAP
        Router[Router] --> TAP[Physical TAP]
        TAP -->|Normal Traffic| Switch2[Switch]
        TAP -.->|Perfect Physical Copy| Monitor2[Security Monitor]
    end
```

## 3. Implementation
There is no code for this, as it is a physical/networking configuration. However, we can simulate the concept in Python to understand how traffic copying works conceptually:

```python
class NetworkSwitch:
    def __init__(self):
        self.span_port = None

    def configure_span(self, monitor_device):
        self.span_port = monitor_device
        print("SPAN Port configured. Copying traffic to monitor.")

    def route_traffic(self, packet, destination):
        # 1. Normal routing
        print(f"Routing '{packet}' to {destination}")
        
        # 2. SPAN / Mirroring logic
        if self.span_port:
            print(f"--> SPAN PORT COPY: Sending copy of '{packet}' to {self.span_port}")

switch = NetworkSwitch()
switch.configure_span("Zeek_IDS_Sensor")
switch.route_traffic("GET /bank_details HTTP/1.1", "Web_Server")
```

## 4. Line-by-Line Explanation
1. `class NetworkSwitch:`: Simulates a network switch.
2. `self.span_port = None`: By default, mirroring is off.
3. `def configure_span(self, monitor_device):`: Tells the switch which device should receive the copied traffic.
4. `def route_traffic(...)`: Simulates a packet passing through the switch.
5. `print(...)`: Represents the packet successfully going to its normal destination.
6. `if self.span_port:`: Checks if mirroring is turned on.
7. `print(...)`: If on, it sends an exact copy of the data to the security monitor.

## 5. Summary
Taps and SPAN ports are the physical and logical mechanisms used to feed network traffic into security tools. Taps are physical, fail-safe devices that guarantee 100% visibility, while SPAN ports use software on a switch to mirror traffic, which is cheaper but can drop packets if the switch gets too busy.
""",
    "028": r"""# Module 28: PCAP Analysis (Wireshark)
## 1. What is it? (Explain from scratch for a complete beginner)
**PCAP (Packet Capture)** is a file format that stores recorded network traffic. Think of it like an audio recording of a phone call, but for computers. **Wireshark** is the most famous tool used to open, read, and analyze these PCAP files. If a hacker breaches your system, you can open the PCAP file in Wireshark to read exactly what commands they typed, what files they stole, and how they got in.

## 2. System Architecture
```mermaid
flowchart TD
    Network[Live Network] --> TCPDump[TCPDump / Capture Tool]
    TCPDump -->|Saves to| PCAP[(capture.pcap File)]
    PCAP --> Wireshark[Wireshark GUI]
    Wireshark -->|Filters applied| Analyst[Analyst reads plain text traffic]
```

## 3. Implementation
While Wireshark is a GUI tool, we can use the Python library `scapy` to programmatically analyze a PCAP file or live packets. Here is how you extract basic info from a packet using Python:

```python
from scapy.all import IP, TCP, rdpcap

def analyze_packet_concept():
    # Simulating a captured packet (IP layer + TCP layer + Raw Data)
    simulated_packet = IP(src="192.168.1.10", dst="10.0.0.5") / TCP(dport=80) / b"GET /admin_login HTTP/1.1"
    
    # Analyze it like Wireshark would
    if IP in simulated_packet:
        source = simulated_packet[IP].src
        destination = simulated_packet[IP].dst
        print(f"Source IP: {source}")
        print(f"Dest IP:   {destination}")
        
    if TCP in simulated_packet:
        print(f"Dest Port: {simulated_packet[TCP].dport}")
        
    if simulated_packet.haslayer('Raw'):
        print(f"Payload:   {simulated_packet.getlayer('Raw').load.decode('utf-8')}")

analyze_packet_concept()
```

## 4. Line-by-Line Explanation
1. `from scapy.all import IP, TCP`: Imports Scapy, a powerful Python tool for packet manipulation.
2. `simulated_packet = ...`: We manually craft a network packet to simulate reading one from a PCAP file. It has an IP address, a TCP port (80 for HTTP), and raw text payload.
3. `if IP in simulated_packet:`: Checks if the packet contains Internet Protocol data.
4. `simulated_packet[IP].src`: Extracts the sender's IP address.
5. `if TCP in simulated_packet:`: Checks if it uses the TCP protocol.
6. `simulated_packet.haslayer('Raw')`: Checks if there is actual application data (like a web request) inside the packet.
7. `...load.decode('utf-8')`: Extracts the raw text, decoding it so it is human-readable.

## 5. Summary
PCAP files are the ultimate source of truth in network security, containing the raw bytes of communication. Tools like Wireshark (and Python's Scapy) allow security analysts to dissect these files packet-by-packet to uncover the exact anatomy of a cyberattack.
""",
    "029": r"""# Module 29: Behavioral Heuristics vs Signatures
## 1. What is it? (Explain from scratch for a complete beginner)
Antiviruses and security tools catch bad guys in two main ways. 
**Signatures** are like police "Wanted" posters. If a file's fingerprint perfectly matches a known virus on the poster, it's blocked. But what if the hacker creates a brand new virus? The signature won't match.
That's where **Behavioral Heuristics** come in. This is like a security guard watching how someone *acts*. If a brand new program suddenly tries to quietly delete all your backup files and encrypt your hard drive, the behavioral engine stops it, not because it recognizes the program's face, but because its *behavior* is malicious.

## 2. System Architecture
```mermaid
flowchart TD
    File[New File Executed]
    File --> SigCheck{Signature Check}
    SigCheck -->|Match found| Block1[Block (Known Malware)]
    SigCheck -->|No match| BehaviorCheck{Behavioral Analysis Engine}
    BehaviorCheck -->|Acts suspiciously| Block2[Block (Zero-Day Malware)]
    BehaviorCheck -->|Acts normal| Allow[Allow Execution]
```

## 3. Implementation
Here is a Python script demonstrating the difference between checking a signature (hash) and checking behavior (actions):

```python
class SecurityAgent:
    def __init__(self):
        self.known_signatures = ["bad_hash_123", "virus_hash_456"]
    
    def scan_file(self, file_hash, file_actions):
        # 1. Signature Analysis
        if file_hash in self.known_signatures:
            return "BLOCKED: Known signature matched!"
            
        # 2. Behavioral Heuristics Analysis
        suspicious_score = 0
        for action in file_actions:
            if action == "disable_antivirus":
                suspicious_score += 50
            if action == "encrypt_files":
                suspicious_score += 50
                
        if suspicious_score >= 100:
            return "BLOCKED: Suspicious behavior detected (Ransomware-like)!"
            
        return "ALLOWED: File appears safe."

agent = SecurityAgent()

# Scenario 1: Known virus
print("Test 1:", agent.scan_file("virus_hash_456", ["print_hello"]))

# Scenario 2: Brand new virus (Zero-day) doing bad things
print("Test 2:", agent.scan_file("brand_new_hash_999", ["disable_antivirus", "encrypt_files"]))

# Scenario 3: Normal program
print("Test 3:", agent.scan_file("good_hash_001", ["read_config_file", "show_ui"]))
```

## 4. Line-by-Line Explanation
1. `class SecurityAgent:`: Represents our antivirus software.
2. `self.known_signatures = [...]`: A database of known "Wanted" posters (file hashes).
3. `def scan_file(self, file_hash, file_actions):`: Examines both the file's ID (hash) and what it tries to do.
4. `if file_hash in self.known_signatures:`: **Signature Check.** If the hash matches, block it instantly.
5. `suspicious_score = 0`: **Behavior Check.** We start keeping a score of how shady the program acts.
6. `if action == "disable_antivirus": suspicious_score += 50`: Legitimate programs rarely do this.
7. `if suspicious_score >= 100:`: If it crosses a threshold, block it, even if we've never seen the file hash before.

## 5. Summary
While signature-based detection is fast and perfectly accurate for known threats, it is useless against new, unseen malware. Behavioral heuristics analyze what a program attempts to do, allowing security systems to catch brand new "zero-day" attacks based purely on malicious actions.
""",
    "030": r"""# Module 30: Threat Intelligence Fusion
## 1. What is it? (Explain from scratch for a complete beginner)
**Threat Intelligence** is information about hackers, their tools, and their IP addresses. **Fusion** is the process of taking threat intelligence from many different sources (the FBI, cybersecurity companies, open-source lists) and combining it into one central system. Your security tools (like your SIEM or Firewall) then consume this "fused" list. If the FBI reports a new Russian hacking server IP, your Threat Intelligence Fusion center instantly updates your firewall to block it, before the hacker ever targets you.

## 2. System Architecture
```mermaid
flowchart LR
    Gov[Gov Intel (FBI/CISA)] --> Fusion[Threat Intel Platform (TIP)]
    Private[Private Vendors (CrowdStrike)] --> Fusion
    OSINT[Open Source Feeds] --> Fusion
    Fusion -->|Consolidated Blocklist| FW[Firewall]
    Fusion -->|Indicators of Compromise| SIEM[SIEM]
```

## 3. Implementation
Here is a Python script showing how a Fusion system might pull IP addresses from multiple feeds, remove duplicates, and generate a master blocklist:

```python
def fetch_gov_intel():
    return ["198.51.100.1", "203.0.113.5"] # Simulated data

def fetch_osint_intel():
    return ["203.0.113.5", "104.28.1.1"] # Notice the duplicate

def threat_intelligence_fusion():
    print("Initiating Threat Intel Fusion...")
    
    # 1. Gather data from all sources
    gov_ips = fetch_gov_intel()
    osint_ips = fetch_osint_intel()
    
    # 2. Fuse and deduplicate (using a Python Set)
    master_blocklist = set()
    master_blocklist.update(gov_ips)
    master_blocklist.update(osint_ips)
    
    print(f"Fusion Complete. Generated Master Blocklist with {len(master_blocklist)} unique IPs.")
    
    # 3. Deploy to security tools
    print("Deploying to Firewall...")
    for ip in master_blocklist:
        print(f" -> Adding FW Block Rule: {ip}")

threat_intelligence_fusion()
```

## 4. Line-by-Line Explanation
1. `def fetch_gov_intel():`: Simulates downloading a threat list from a government agency.
2. `def fetch_osint_intel():`: Simulates downloading a list from an open-source community.
3. `master_blocklist = set()`: Creates a Python `set`. Sets are data structures that automatically remove duplicate entries.
4. `master_blocklist.update(gov_ips)`: Adds the government IPs to the set.
5. `master_blocklist.update(osint_ips)`: Adds the OSINT IPs. The duplicate "203.0.113.5" is ignored automatically.
6. `for ip in master_blocklist:`: Loops through the final, clean list of bad IP addresses.
7. `print(f" -> Adding FW Block Rule: {ip}")`: Simulates sending an API command to the firewall to block the bad guys.

## 5. Summary
Threat Intelligence Fusion takes raw data about cyber threats from multiple global sources, cleans it, and transforms it into actionable, automated defense. It allows organizations to proactively protect themselves based on the experiences and intelligence gathered by the rest of the world.
"""
}

for mod_id, mod_content in modules.items():
    file_path = os.path.join(out_dir, f"module_{mod_id}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(mod_content)
        
print("Successfully generated all 10 modules.")
