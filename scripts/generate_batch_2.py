import os

output_dir = r"E:\cyberos-prototype\educational_dashboard\raw_modules"
os.makedirs(output_dir, exist_ok=True)

modules = {
    "011": """# Module 11: The History of Network Attacks
## 1. What is it? (Explain from scratch for a complete beginner)
The history of network attacks is the story of how computer networks evolved from trusted academic environments into contested digital battlegrounds. Early networks assumed all users were friendly, meaning there was little to no security built into the original protocols. Over time, as the internet grew, individuals discovered they could abuse these protocols to gain unauthorized access, steal data, or disrupt services. Studying historical attacks like the Morris Worm (1988) or ILOVEYOU (2000) helps us understand why modern security defenses are built the way they are today.

## 2. Attack Architecture / Flow
```mermaid
sequenceDiagram
    participant A as Attacker
    participant VS as Vulnerable System
    participant N as Network
    A->>VS: Send malicious payload/worm
    VS-->>A: Compromise successful
    VS->>N: Self-replicate & scan for others
    N->>VS: Network congestion / Denial of Service
```

## 3. Implementation / Code
```python
# Defensive Code: Legacy Attack Pattern Detector (Heuristic)
def detect_legacy_patterns(log_lines):
    suspicious_patterns = ["DEBUG", "WIZ", "expn", "vrfy"]
    alerts = []
    
    for line in log_lines:
        line_lower = line.lower()
        for pattern in suspicious_patterns:
            if pattern in line_lower:
                alerts.append(f"ALERT: Historical attack footprint detected: {pattern} in log -> {line}")
                
    return alerts

# Example Usage
logs = ["Jan 10 08:30:00 server postfix/smtpd: connect from unknown",
        "Jan 10 08:31:00 server sendmail: DEBUG root"]
print(detect_legacy_patterns(logs))
```

## 4. Line-by-Line Explanation
- `def detect_legacy_patterns(log_lines):`: Defines our defensive function that takes a list of server logs.
- `suspicious_patterns = [...]`: A list of commands historically abused in older protocols (like SMTP or Telnet).
- `alerts = []`: Creates an empty list to store our security warnings.
- `for line in log_lines:`: Loops through every line in our server logs.
- `if pattern in line_lower:`: Checks if the suspicious historical command is present in the current log line.
- `alerts.append(...)`: If found, it creates an alert string and adds it to our list.

## 5. Summary
By analyzing the history of network attacks, we learn that security cannot be an afterthought. Defensive programming, such as looking for deprecated or dangerous commands in logs, is a foundational step in securing legacy systems against known historical footprints.
""",

    "012": """# Module 12: Reconnaissance & Port Scanning (Nmap)
## 1. What is it? (Explain from scratch for a complete beginner)
Reconnaissance is the "scouting" phase of a cyber attack. Just like a burglar checking which doors and windows of a house are unlocked, an attacker scans a target network to see which "ports" (communication channels) are open. Tools like Nmap send tiny network messages to thousands of ports on a server. If the server replies, the attacker knows that specific port is open and potentially vulnerable. Port scanning itself isn't an attack, but it is the critical first step an attacker takes to map out their target.

## 2. Attack Architecture / Flow
```mermaid
sequenceDiagram
    participant A as Attacker (Scanner)
    participant F as Target Firewall/Server
    A->>F: SYN Packet (Port 80)
    F-->>A: SYN/ACK (Port 80 is Open!)
    A->>F: RST (Never mind, just checking)
    A->>F: SYN Packet (Port 22)
    F-->>A: RST/ACK (Port 22 is Closed!)
```

## 3. Implementation / Code
```python
# Defensive Code: Port Scan Detection via Connection Rate Tracking
from collections import defaultdict
import time

class PortScanDetector:
    def __init__(self, time_window=60, port_threshold=20):
        self.time_window = time_window
        self.port_threshold = port_threshold
        # Stores {source_ip: {port1, port2, ...}}
        self.connections = defaultdict(set)
        
    def log_connection(self, src_ip, dst_port):
        self.connections[src_ip].add(dst_port)
        
        # Check if the unique ports scanned exceed our threshold
        if len(self.connections[src_ip]) > self.port_threshold:
            print(f"[!] PORT SCAN DETECTED from {src_ip}: {len(self.connections[src_ip])} unique ports.")

# Example Usage
detector = PortScanDetector()
for port in range(1, 25):
    detector.log_connection("192.168.1.100", port)
```

## 4. Line-by-Line Explanation
- `from collections import defaultdict`: Imports a specialized dictionary that automatically handles missing keys.
- `class PortScanDetector:`: Creates a blueprint for our defensive tool.
- `self.time_window = time_window`: Sets how long we track connections (e.g., 60 seconds).
- `self.connections = defaultdict(set)`: A dictionary mapping an IP address to a unique mathematical 'set' of ports it has touched.
- `self.connections[src_ip].add(dst_port)`: Records the destination port accessed by the source IP. Sets naturally prevent duplicates.
- `if len(...) > self.port_threshold:`: If one IP touches more than 20 distinct ports quickly, we flag it as a scanner.

## 5. Summary
Reconnaissance helps attackers find ways in, but defenders can use the noise generated by tools like Nmap to their advantage. By tracking how many unique ports a single IP addresses attempts to access in a short timeframe, we can detect and block scanners before they find vulnerabilities.
""",

    "013": """# Module 13: Botnets & The Zombie Army
## 1. What is it? (Explain from scratch for a complete beginner)
A botnet (short for "robot network") is a massive army of infected computers, smart TVs, and IoT cameras controlled by a single attacker (the "botmaster"). The owners of these devices usually have no idea their device is infected. The botmaster can issue a command to all these "zombie" devices at once, ordering them to simultaneously flood a target website with traffic, send billions of spam emails, or mine cryptocurrency.

## 2. Attack Architecture / Flow
```mermaid
flowchart TD
    A["Attacker (Botmaster)"] -->|Issues Command| C2["Command & Control Server"]
    C2 -->|Relays Command| B1["Infected PC (Zombie)"]
    C2 -->|Relays Command| B2["Infected IoT Camera (Zombie)"]
    C2 -->|Relays Command| B3["Infected Smart Fridge (Zombie)"]
    B1 -->|Attacks| T["Target Server"]
    B2 -->|Attacks| T
    B3 -->|Attacks| T
```

## 3. Implementation / Code
```python
# Defensive Code: Detecting Distributed Anomalies (Botnet DDoS Simulation)
from collections import Counter

def detect_botnet_activity(network_logs, traffic_threshold=1000):
    # network_logs = [{'src_ip': '...', 'dst_ip': '...', 'bytes': ...}]
    target_traffic = Counter()
    
    # Aggregate total connections to each destination
    for log in network_logs:
        target_traffic[log['dst_ip']] += 1
        
    alerts = []
    for target_ip, connection_count in target_traffic.items():
        if connection_count > traffic_threshold:
            alerts.append(f"[!] Botnet/DDoS Alert: {target_ip} is receiving massive distributed traffic ({connection_count} connections).")
            
    return alerts

# Example Usage
logs = [{'src_ip': f"10.0.0.{i}", 'dst_ip': "192.168.1.50", 'bytes': 64} for i in range(1500)]
print(detect_botnet_activity(logs))
```

## 4. Line-by-Line Explanation
- `from collections import Counter`: Imports a built-in Python tool used specifically for counting occurrences.
- `def detect_botnet_activity(...)`: Defines our detection function, taking a list of network logs and a threshold.
- `target_traffic = Counter()`: Initializes a counter to track how many connections each server is receiving.
- `for log in network_logs:`: Loops through all network traffic data.
- `target_traffic[log['dst_ip']] += 1`: Increments the connection count for the destination IP by 1.
- `if connection_count > traffic_threshold:`: Checks if a single destination is receiving an abnormal, massive amount of connections, indicative of a coordinated botnet attack.

## 5. Summary
Botnets leverage the combined power of thousands of infected devices to overwhelm targets. Defenders protect networks from botnets by using aggregation and thresholding algorithms to spot when a single target is suddenly hit by distributed, anomalous traffic volumes.
""",

    "014": """# Module 14: Command & Control (C2) Beacons
## 1. What is it? (Explain from scratch for a complete beginner)
When malware infects a computer, it usually needs instructions on what to do next (e.g., "steal passwords," "encrypt files," or "wait"). To get these instructions, the malware "calls home" to the attacker's Command & Control (C2) server. To avoid detection, it doesn't keep a connection open all the time. Instead, it checks in briefly at regular intervals—say, every 5 minutes. This rhythmic, heartbeat-like check-in is called a "beacon." 

## 2. Attack Architecture / Flow
```mermaid
sequenceDiagram
    participant I as Infected Host
    participant C2 as C2 Server
    Note over I: Host is infected
    loop Every 60 seconds (Beaconing)
        I->>C2: HTTP GET /update (I am alive)
        C2-->>I: 200 OK (Sleep for 60s)
    end
    I->>C2: HTTP GET /update (I am alive)
    C2-->>I: 200 OK (Download ransomware module)
```

## 3. Implementation / Code
```python
# Defensive Code: Detecting C2 Beaconing via Time Variance Analysis
import statistics

def detect_c2_beacons(connection_timestamps, variance_threshold=2.0):
    if len(connection_timestamps) < 3:
        return False, "Not enough data"
        
    # Calculate the time difference (delta) between consecutive connections
    deltas = []
    for i in range(1, len(connection_timestamps)):
        deltas.append(connection_timestamps[i] - connection_timestamps[i-1])
        
    # Calculate the variance of these time differences
    time_variance = statistics.variance(deltas)
    
    # If the variance is very low, the connections are suspiciously rhythmic
    if time_variance < variance_threshold:
        return True, f"Suspicious Beaconing Detected! Variance: {time_variance:.2f}"
    
    return False, f"Normal human traffic. Variance: {time_variance:.2f}"

# Example Usage: Connections happening almost exactly every 60 seconds
timestamps = [1000, 1060, 1121, 1180, 1240, 1301]
is_c2, msg = detect_c2_beacons(timestamps)
print(msg)
```

## 4. Line-by-Line Explanation
- `import statistics`: Imports Python's math library for calculating variance.
- `def detect_c2_beacons(...)`: The function takes a list of times a computer connected to a specific external domain.
- `deltas.append(connection_timestamps[i] - connection_timestamps[i-1])`: Computes the exact time gap between each consecutive connection.
- `time_variance = statistics.variance(deltas)`: Calculates how much these gaps differ from one another.
- `if time_variance < variance_threshold:`: Normal human browsing is highly random (high variance). If the variance is extremely low, it means the connection is automated and rhythmic—a classic sign of C2 beaconing.

## 5. Summary
Malware needs to communicate with attackers to be effective. By analyzing the timing of network connections, defenders can spot the robotic, rhythmic "heartbeat" of C2 beacons hiding within the noise of normal human web browsing.
""",

    "015": """# Module 15: Volumetric DDoS & TCP Exhaustion
## 1. What is it? (Explain from scratch for a complete beginner)
Imagine a restaurant that takes reservations over the phone. If a group of pranksters repeatedly call the restaurant, start a reservation, but hang up before finishing, all the phone lines get tied up. Real customers can't get through, and the host is left waiting for the pranksters to finish their sentences. This is a TCP SYN Flood attack. The attacker starts thousands of network "handshakes" (SYN) with a server but never finishes them. The server exhausts its memory waiting for the final handshake (ACK), causing it to crash or ignore legitimate users.

## 2. Attack Architecture / Flow
```mermaid
sequenceDiagram
    participant A as Attacker
    participant S as Web Server
    A->>S: SYN (I want to connect)
    S-->>A: SYN-ACK (Okay, waiting for your confirmation...)
    Note over A, S: Attacker ignores the response
    A->>S: SYN (I want to connect)
    S-->>A: SYN-ACK (Okay, waiting for your confirmation...)
    Note over S: Server runs out of connection memory!
```

## 3. Implementation / Code
```python
# Defensive Code: Detecting SYN Flood attacks by tracking TCP flags
def detect_syn_flood(packet_logs, max_unanswered_syns=500):
    # Track the difference between SYNs received and ACKs completed per IP
    pending_connections = {}
    
    for packet in packet_logs:
        src = packet['src_ip']
        flags = packet['tcp_flags']
        
        if src not in pending_connections:
            pending_connections[src] = 0
            
        if flags == 'SYN':
            pending_connections[src] += 1
        elif flags == 'ACK':
            pending_connections[src] -= 1
            
    # Check for IPs with too many uncompleted handshakes
    for ip, uncompleted in pending_connections.items():
        if uncompleted > max_unanswered_syns:
            print(f"[!] SYN FLOOD ALERT: {ip} has {uncompleted} half-open connections!")

# Example Usage
logs = [{'src_ip': '10.9.9.9', 'tcp_flags': 'SYN'} for _ in range(600)]
detect_syn_flood(logs)
```

## 4. Line-by-Line Explanation
- `def detect_syn_flood(...)`: Defines a function that scans network packets to find attackers exhausting server memory.
- `pending_connections = {}`: A dictionary to keep a running tally of open connections for each IP address.
- `if flags == 'SYN':`: If the packet is a "hello" (SYN), we add 1 to the tally of open connections.
- `elif flags == 'ACK':`: If the packet completes the handshake (ACK), we subtract 1 from the tally.
- `if uncompleted > max_unanswered_syns:`: If a single IP address has opened hundreds of connections but never finished them, we raise an alert.

## 5. Summary
TCP exhaustion attacks exploit the fundamental rules of how computers agree to communicate on the internet. By monitoring the ratio of initiated connections (SYN) to completed connections (ACK), defenders can identify and block IP addresses that are attempting to overwhelm the server's memory.
""",

    "016": """# Module 16: UDP Amplification Attacks
## 1. What is it? (Explain from scratch for a complete beginner)
Imagine sending a letter to a mail-order catalog company requesting their heaviest 500-page catalog. But instead of putting *your* return address on the envelope, you put the address of your enemy. The company sends the massive heavy catalog to your enemy. Now imagine doing this thousands of times. This is a UDP Amplification attack. An attacker sends a tiny request to a public server (like a DNS or NTP server) using a forged (spoofed) IP address of their victim. The public server replies with a massive chunk of data, inadvertently flooding and destroying the victim's internet connection.

## 2. Attack Architecture / Flow
```mermaid
sequenceDiagram
    participant A as Attacker
    participant S as Vulnerable Public Server (NTP/DNS)
    participant V as Victim
    A->>S: 10 Bytes Request (Spoofed Source = Victim IP)
    S-->>V: 3000 Bytes Response
    A->>S: 10 Bytes Request (Spoofed Source = Victim IP)
    S-->>V: 3000 Bytes Response
    Note over V: Victim's bandwidth is completely saturated
```

## 3. Implementation / Code
```python
# Defensive Code: Detecting UDP Amplification based on inbound payload size and ports
def detect_udp_amplification(inbound_traffic):
    # Common ports abused for amplification (DNS, NTP, SSDP, Memcached)
    amplification_ports = {53, 123, 1900, 11211}
    threshold_bytes_per_sec = 5_000_000  # 5 MB/s
    
    victim_traffic_volume = {}
    
    for packet in inbound_traffic:
        if packet['protocol'] == 'UDP' and packet['src_port'] in amplification_ports:
            dst = packet['dst_ip']
            victim_traffic_volume[dst] = victim_traffic_volume.get(dst, 0) + packet['size_bytes']
            
    for victim_ip, volume in victim_traffic_volume.items():
        if volume > threshold_bytes_per_sec:
            print(f"[!] UDP Amplification Detected! {victim_ip} received {volume} bytes from amplification ports.")

# Example Usage
traffic = [{'protocol': 'UDP', 'src_port': 123, 'dst_ip': '192.168.1.10', 'size_bytes': 4000} for _ in range(2000)]
detect_udp_amplification(traffic)
```

## 4. Line-by-Line Explanation
- `amplification_ports = {53, 123, 1900, 11211}`: Sets containing the specific server ports commonly tricked into sending massive responses.
- `threshold_bytes_per_sec = 5_000_000`: Sets a baseline. If an internal IP receives more than 5MB per second of this specific UDP traffic, it's abnormal.
- `if packet['protocol'] == 'UDP' and packet['src_port'] in amplification_ports:`: Filters the traffic. We only care about UDP traffic originating from the risky ports.
- `victim_traffic_volume.get(dst, 0) + packet['size_bytes']`: Adds the size of the incoming packet to the running total for that victim's IP.
- `if volume > threshold_bytes_per_sec:`: Triggers the alarm if the volume exceeds safe limits.

## 5. Summary
UDP Amplification allows attackers to multiply their destructive power without needing a massive botnet. Defenders must monitor inbound UDP traffic from known vulnerable services (like DNS and NTP) to quickly detect and mitigate these massive volumetric floods.
""",

    "017": """# Module 17: Application Layer Attacks (Slowloris)
## 1. What is it? (Explain from scratch for a complete beginner)
Unlike volumetric DDoS attacks that try to overwhelm a server with sheer force and millions of packets, Slowloris is a "low and slow" attack. Imagine someone walking up to a bank teller and speaking incredibly slowly, taking five minutes between every single word. The teller cannot help anyone else while they wait for the person to finish their sentence. Slowloris does this to web servers. It opens a web connection and sends pieces of a request at a painfully slow pace, keeping the server's connection slots occupied until legitimate users are entirely blocked out.

## 2. Attack Architecture / Flow
```mermaid
sequenceDiagram
    participant A as Attacker
    participant S as Web Server
    A->>S: HTTP GET / (Partial Header)
    Note over S: Server waits for the rest of the request
    loop Every 10 seconds
        A->>S: Send one more character: "X-Header: keep-alive"
        Note over S: Server resets timeout, keeps waiting...
    end
    Note over S: Server hits maximum concurrent connections. Goes offline.
```

## 3. Implementation / Code
```python
# Defensive Code: Detecting Slowloris via Connection Timeout & Byte Rate
def detect_slowloris(active_connections, current_time):
    # Minimum bytes per second a legitimate client should send
    min_bytes_per_sec = 10
    
    for conn_id, conn_data in active_connections.items():
        duration = current_time - conn_data['start_time']
        
        # Only evaluate connections open longer than 30 seconds
        if duration > 30:
            bytes_per_sec = conn_data['bytes_received'] / duration
            
            if bytes_per_sec < min_bytes_per_sec:
                print(f"[!] Slowloris Alert! Connection {conn_id} is suspiciously slow: {bytes_per_sec:.2f} B/s. Terminating.")

# Example Usage
# Connection 1: Open for 45 seconds, but only sent 50 bytes total.
conns = {
    "conn_001": {'start_time': 100, 'bytes_received': 50}
}
detect_slowloris(conns, current_time=145)
```

## 4. Line-by-Line Explanation
- `min_bytes_per_sec = 10`: Defines our standard. Legitimate web requests transfer data much faster than 10 bytes a second.
- `duration = current_time - conn_data['start_time']`: Calculates exactly how many seconds the connection has been held open.
- `if duration > 30:`: Gives clients a grace period. We only analyze connections that have been open for an unusually long time.
- `bytes_per_sec = conn_data['bytes_received'] / duration`: Calculates the average speed of data transfer for this connection.
- `if bytes_per_sec < min_bytes_per_sec:`: If a connection is open a long time but transferring almost no data, it matches the Slowloris profile.

## 5. Summary
Application layer attacks like Slowloris prove that you don't need a massive amount of bandwidth to take down a server. Defenders must enforce strict timeouts and minimum data-transfer rates to prevent attackers from hoarding server resources with "low and slow" techniques.
""",

    "018": """# Module 18: Data Exfiltration
## 1. What is it? (Explain from scratch for a complete beginner)
Data Exfiltration is the cyber equivalent of smuggling. Once an attacker has broken into a network and found sensitive data (like credit card numbers or secret blueprints), they have to get it out of the network without sounding the alarm. Because firewalls block incoming attacks, attackers often encrypt the stolen data and send it outbound, hiding it in normal-looking web traffic or file transfers so the security team thinks it's just an employee uploading a document.

## 2. Attack Architecture / Flow
```mermaid
sequenceDiagram
    participant I as Infected Internal Host
    participant F as Corporate Firewall
    participant A as Attacker Server
    Note over I: Gathers sensitive internal files
    I->>I: Zips and Encrypts files
    I->>F: Outbound HTTPS traffic (Looks normal)
    F->>A: Forwards traffic
    Note over A: Attacker receives stolen data
```

## 3. Implementation / Code
```python
# Defensive Code: Baseline Outbound Traffic Anomaly Detection
def detect_exfiltration(daily_outbound_logs, baseline_mb=500, spike_multiplier=3):
    alerts = []
    
    for host_ip, bytes_sent in daily_outbound_logs.items():
        mb_sent = bytes_sent / (1024 * 1024)
        
        # If the host exceeds normal daily limits drastically
        if mb_sent > (baseline_mb * spike_multiplier):
            alerts.append(f"[CRITICAL] Exfiltration Alert: {host_ip} transferred {mb_sent:.2f} MB outbound! Normal is ~{baseline_mb} MB.")
            
    return alerts

# Example Usage
logs = {
    "10.0.0.15": 104857600,   # 100 MB (Normal)
    "10.0.0.99": 5368709120   # 5120 MB (Suspicious!)
}
for alert in detect_exfiltration(logs):
    print(alert)
```

## 4. Line-by-Line Explanation
- `baseline_mb=500`: Establishes that an average employee uploads about 500 MB of data to the internet per day.
- `spike_multiplier=3`: Sets a threshold. If someone uploads 3 times the baseline, it's highly suspicious.
- `mb_sent = bytes_sent / (1024 * 1024)`: Converts raw network bytes into readable Megabytes.
- `if mb_sent > (baseline_mb * spike_multiplier):`: Compares the host's daily outbound traffic against the established maximum threshold.
- `alerts.append(...)`: Generates a critical alert pointing directly to the IP address hoarding and smuggling data out of the network.

## 5. Summary
Preventing intruders from breaking in is only half the battle. Monitoring outbound traffic to detect anomalies and massive data transfers is critical for stopping Data Exfiltration. If you catch the smuggling attempt, the attacker leaves empty-handed.
""",

    "019": """# Module 19: DNS Tunneling
## 1. What is it? (Explain from scratch for a complete beginner)
DNS (Domain Name System) is the phonebook of the internet; it turns names like "google.com" into IP addresses. Because almost every network allows DNS traffic to flow freely, attackers use it as a secret tunnel. Instead of asking for a real website, malware asks for a fake website containing hidden, stolen data (e.g., "password123.attacker.com"). The firewall sees a "normal" DNS request and lets it through. The attacker's server receives the request, strips off the data ("password123"), and replies with commands disguised as a DNS response.

## 2. Attack Architecture / Flow
```mermaid
sequenceDiagram
    participant I as Infected Host
    participant D as Corporate DNS
    participant A as Attacker DNS Server
    Note over I: Steals data: "secret_file"
    I->>D: DNS Query: "secret_file.attacker.com"
    D->>A: Forwards Query: "secret_file.attacker.com"
    Note over A: Extracts "secret_file"
    A-->>D: DNS Response: 192.168.x.x (Secret Command)
    D-->>I: Forwards response back to malware
```

## 3. Implementation / Code
```python
# Defensive Code: Detecting DNS Tunneling via Subdomain Length and Entropy
import math

def calculate_entropy(string):
    # Calculates the randomness (entropy) of a string.
    prob = [float(string.count(c)) / len(string) for c in set(string)]
    return -sum(p * math.log(p, 2) for p in prob)

def detect_dns_tunneling(dns_queries, length_threshold=45, entropy_threshold=4.0):
    for query in dns_queries:
        # Extract just the subdomain part (e.g., 'a8b7c6d5e4' from 'a8b7c6d5e4.evil.com')
        subdomain = query.split('.')[0]
        
        # Tunneling usually uses very long, random-looking subdomains to fit data
        if len(subdomain) > length_threshold or calculate_entropy(subdomain) > entropy_threshold:
            print(f"[!] DNS Tunneling Alert: Highly suspicious query -> {query}")

# Example Usage
queries = ["www.google.com", "mail.yahoo.com", "z3x9v2b4n7m1q8w5e2r0.attacker.com"]
detect_dns_tunneling(queries)
```

## 4. Line-by-Line Explanation
- `def calculate_entropy(string):`: A mathematical function that measures how "random" a string looks. Normal words have low entropy; encrypted data has high entropy.
- `subdomain = query.split('.')[0]`: Takes a full web address and isolates the very first part (the subdomain).
- `if len(subdomain) > length_threshold...`: Attackers need to stuff a lot of data into the subdomain, making it unnaturally long. This checks if it's too long.
- `or calculate_entropy(subdomain) > entropy_threshold:`: Checks if the subdomain looks like random garbage (encrypted data) rather than a real word like "mail" or "www".
- `print(...)`: Alerts the security team to the covert tunnel.

## 5. Summary
Attackers love DNS tunneling because DNS is rarely blocked or deeply inspected by firewalls. By applying mathematical concepts like entropy and length thresholds, defenders can spot encrypted data masquerading as normal internet phonebook lookups.
""",

    "020": """# Module 20: IP Spoofing
## 1. What is it? (Explain from scratch for a complete beginner)
When you send a physical letter, you write your return address in the top left corner. But nothing stops you from writing someone else's address there. IP Spoofing is the digital version of this. An attacker alters the network packet to forge the "Source IP address." They do this to hide their true identity, bypass firewalls that only trust specific IPs, or to trick servers into sending massive amounts of data to a victim (as seen in UDP Amplification). 

## 2. Attack Architecture / Flow
```mermaid
flowchart LR
    A["Attacker (Real IP: 1.1.1.1)"] -- "Forges Packet: SRC=8.8.8.8" --> R["Router/Internet"]
    R -- "Delivers Spoofed Packet" --> T["Target Server"]
    T -- "Replies to Forged Address" --> V["Victim (IP: 8.8.8.8)"]
```

## 3. Implementation / Code
```python
# Defensive Code: Ingress Filtering (Anti-Spoofing Pseudo-code)
def verify_ingress_traffic(packet, interface_expected_subnet):
    '''
    Simulates a router interface checking if the source IP of a packet 
    actually belongs to the network connected to that interface.
    '''
    src_ip = packet['src_ip']
    
    # In a real scenario, this uses IP math (CIDR). We use a basic string check for simplicity.
    if src_ip.startswith(interface_expected_subnet):
        return "Packet Accepted: Source IP matches interface routing rules."
    else:
        # BCP38: Network Ingress Filtering principle
        return f"[!] SPOOFING DETECTED: Packet dropped. {src_ip} shouldn't come from this interface!"

# Example Usage
# Router Interface 1 is connected to the 10.0.0.x network.
valid_packet = {'src_ip': '10.0.0.5', 'dst_ip': '8.8.8.8'}
spoofed_packet = {'src_ip': '192.168.1.1', 'dst_ip': '8.8.8.8'}

print(verify_ingress_traffic(valid_packet, "10.0.0."))
print(verify_ingress_traffic(spoofed_packet, "10.0.0."))
```

## 4. Line-by-Line Explanation
- `def verify_ingress_traffic(...)`: Defines a function representing a security check on a router interface.
- `interface_expected_subnet`: Represents the valid IP addresses that exist on the network physically plugged into this router port.
- `if src_ip.startswith(interface_expected_subnet):`: Checks if the packet's return address matches the physical location it just came from.
- `return f"[!] SPOOFING DETECTED..."`: If a packet claims to be from an external IP but comes from an internal network cable (or vice versa), the router drops it immediately.

## 5. Summary
IP spoofing undermines trust on the internet. The primary defense against IP spoofing is Network Ingress Filtering (BCP38), where routers strictly verify that traffic entering their interfaces actually belongs to the IP subnets assigned to those interfaces.
"""
}

for mod_id, content in modules.items():
    file_path = os.path.join(output_dir, f"module_{mod_id}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content.strip())

print(f"Successfully generated {len(modules)} educational modules in {output_dir}")
