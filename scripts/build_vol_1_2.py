import os

OUTPUT_DIR = r"E:\cyberos-prototype\cyberos-docs\docs\handbook"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def write_file(filename, content):
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# ==========================================
# VOLUME 1: FOUNDATIONS OF CYBERSPACE
# ==========================================
VOL1_CONTENT = """
# Volume 1: The Foundations of Cyberspace

## Chapter 1: The Anatomy of a Network
To understand how CyberOS defends a network, we must first understand what a network is from absolute zero. A network is a collection of computers, servers, mainframes, network devices, or other devices connected to one another to allow the sharing of data.

```mermaid
flowchart LR
    PC1[User PC] --> SW[Switch]
    PC2[User PC] --> SW
    SW --> RT[Router]
    RT --> FW[Firewall]
    FW --> INT((Internet))
```
At its core, all data is binary—1s and 0s sent via electrical pulses over copper wire, light pulses over fiber optics, or radio waves via Wi-Fi.

## Chapter 2: The OSI & TCP/IP Models
The Open Systems Interconnection (OSI) model standardizes the communication functions of a telecommunication system without regard to its underlying internal structure.

```mermaid
block-beta
  columns 1
  L7["Layer 7: Application (HTTP, DNS)"]
  L6["Layer 6: Presentation (TLS, SSL)"]
  L5["Layer 5: Session"]
  L4["Layer 4: Transport (TCP, UDP)"]
  L3["Layer 3: Network (IP, ICMP)"]
  L2["Layer 2: Data Link (MAC, Ethernet)"]
  L1["Layer 1: Physical (Cables, Radio)"]
```
CyberOS primarily extracts metadata from Layers 3, 4, and 7.

## Chapter 3: IP Addressing & Subnets
Every device on a network needs a logical address. In IPv4, this is a 32-bit number, usually represented in dotted-decimal format (e.g., `192.168.1.10`). A subnet mask (e.g., `255.255.255.0`) divides the IP address into a network portion and a host portion, dictating how packets are routed locally versus globally.

## Chapter 4: The TCP 3-Way Handshake
The Transmission Control Protocol (TCP) ensures reliable delivery. Before data is sent, a connection must be established. This is the cornerstone of stateful networking.

```mermaid
sequenceDiagram
    participant Client
    participant Server
    Client->>Server: SYN (Synchronize)
    Server->>Client: SYN-ACK (Acknowledge)
    Client->>Server: ACK (Acknowledge)
    Note over Client,Server: Connection Established (ESTABLISHED state)
```

## Chapter 5: UDP - The Best Effort Protocol
Unlike TCP, the User Datagram Protocol (UDP) does not establish a connection. It simply fires packets at the destination. It is fast but unreliable. DNS and video streaming heavily utilize UDP. Because UDP has no state, detecting UDP anomalies requires purely statistical modeling rather than state-tracking.

## Chapter 6: Ports and Sockets
An IP address gets data to the right computer. A **Port** gets data to the right application on that computer. 
* Port 80 = HTTP Web Traffic
* Port 443 = HTTPS Secure Web Traffic
* Port 53 = DNS
An IP address paired with a port (e.g., `192.168.1.10:443`) is called a **Socket**.

## Chapter 7: DNS - The Phonebook of the Internet
Humans cannot remember IP addresses like `142.250.190.46`. We remember `google.com`. The Domain Name System (DNS) translates domains to IP addresses.

```mermaid
sequenceDiagram
    participant PC
    participant Resolver
    participant RootServer
    PC->>Resolver: Where is example.com?
    Resolver->>RootServer: Who handles .com?
    RootServer->>Resolver: Ask the .com TLD server
    Note over Resolver: Resolves address recursively
    Resolver->>PC: example.com is 93.184.216.34
```
*Cyber Context*: Attackers abuse DNS to tunnel data or dynamically locate C2 servers via Domain Generation Algorithms (DGA).

## Chapter 8: HTTP & The Web
Hypertext Transfer Protocol (HTTP) is a Layer 7 protocol used to transmit hypermedia documents, such as HTML. It follows a classic client-server model, where a client opens a connection to make a request, then waits until it receives a response.

## Chapter 9: Encryption, TLS, and SSL
Transport Layer Security (TLS) encrypts HTTP traffic. 
```mermaid
sequenceDiagram
    participant Client
    participant Server
    Client->>Server: ClientHello (Supported Ciphers)
    Server->>Client: ServerHello (Chosen Cipher, Certificate)
    Client->>Server: Key Exchange
    Note over Client,Server: Encrypted Channel Established
```
CyberOS operates under a strict "No Decryption" mandate. We use the unencrypted `ClientHello` metadata (like SNI and JA3 fingerprints) to classify threats.

## Chapter 10: Packets vs. Flows
A **Packet** is a single unit of data. A **Flow** is a sequence of packets between two sockets (Source IP/Port to Dest IP/Port) over a period of time.
Network Detection and Response (NDR) systems like CyberOS analyze flows, not packets. Threats manifest over time; a single packet is rarely malicious on its own, but a sequence of packets reveals intent.
"""

# ==========================================
# VOLUME 2: THE ATTACK SURFACE
# ==========================================
VOL2_CONTENT = """
# Volume 2: The Attack Surface

## Chapter 11: The History of Network Attacks
Cyber threats have evolved from simple defacements in the 1990s to highly automated, state-sponsored botnets today. Modern attacks do not rely on isolated malware binaries; they rely on networked infrastructure. The network is the ultimate source of truth.

## Chapter 12: Reconnaissance & Port Scanning
Before an attacker strikes, they map the target. A port scan systematically probes a server's ports to find open services.

```mermaid
flowchart TD
    A[Attacker] -->|SYN Port 21| T[Target]
    T -->|RST| A
    A -->|SYN Port 22| T
    T -->|SYN-ACK (Open!)| A
    A -->|SYN Port 23| T
    T -->|RST| A
```
*Detection*: CyberOS flags high fan-out (one source to many unique destination ports) over tumbling time windows.

## Chapter 13: Botnets & The Zombie Army
A botnet is a network of compromised computers (zombies) controlled by a single attacker (the Botmaster). They are used to execute coordinated tasks, primarily DDoS attacks.

```mermaid
flowchart TD
    B[Botmaster] --> C2[Command & Control Server]
    C2 --> Z1[Zombie PC]
    C2 --> Z2[Zombie IoT Fridge]
    C2 --> Z3[Zombie Server]
    Z1 --> T[Target Victim]
    Z2 --> T
    Z3 --> T
```

## Chapter 14: Command & Control (C2) Beacons
A compromised host must ask the C2 server for instructions. To bypass firewalls, the host initiates the connection outward periodically. This is called a **Beacon**. 
Mathematical detection relies on Inter-Arrival Time (IAT). If $IAT_{variance} \\approx 0$, the connection is a highly suspicious mechanical beacon.

## Chapter 15: Volumetric DDoS & Amplification
Volumetric attacks overwhelm bandwidth. In an **Amplification Attack**, an attacker sends a small forged packet (e.g., DNS request) to a vulnerable server, which replies with a massive packet sent to the victim.
* **Amplification Factor**: The ratio of the response size to the request size. NTP and Memcached can amplify traffic by 50,000x.

## Chapter 16: TCP State Exhaustion (SYN Floods)
As introduced in Chapter 4, the TCP handshake requires memory. By sending millions of SYN packets but never replying with the final ACK, an attacker fills the server's connection table until it crashes. 
![DDoS Evidence](../../assets/screenshots/dashboard_full.png)
*(CyberOS detecting a massive Volumetric Flood in real-time)*

## Chapter 17: Application Layer Exhaustion (Slowloris)
Unlike a volumetric attack, a Slowloris attack requires virtually no bandwidth. The attacker opens hundreds of valid HTTP connections but sends data at an excruciatingly slow rate (1 byte every 10 seconds). The server keeps the sockets open, eventually exhausting its connection pool.

## Chapter 18: Data Exfiltration
Once an attacker accesses a sensitive database, they must remove the data. Exfiltration often manifests as massive Byte Asymmetry.
$$ Asymmetry = \\frac{Bytes\\ Out}{Bytes\\ In} $$
If a workstation uploads 50GB to an unknown offshore IP but downloads 2MB, it is highly anomalous.

## Chapter 19: DNS Tunneling
Firewalls often block all outbound ports except 80 (HTTP), 443 (HTTPS), and 53 (DNS). Attackers bypass firewalls by encoding stolen data inside DNS queries.
`query: 59382data_chunk_base64.attacker.com`
```mermaid
sequenceDiagram
    participant Victim
    participant DNS_Server
    participant Attacker_C2
    Victim->>DNS_Server: Resolve [STOLEN_DATA].c2.com
    DNS_Server->>Attacker_C2: Ask authoritative server for [STOLEN_DATA].c2.com
    Note over Attacker_C2: Data Extracted!
```

## Chapter 20: IP Spoofing
IP Spoofing is the creation of IP packets with a false source IP address, used to hide the identity of the sender or to impersonate another computing system. This breaks standard rate-limiting firewalls. CyberOS calculates the Shannon Entropy of source IPs to detect randomized spoofing mathematically.
"""

def generate():
    write_file("01_volume_1.md", VOL1_CONTENT)
    write_file("02_volume_2.md", VOL2_CONTENT)
    print("Volumes 1 and 2 (Chapters 1-20) generated successfully.")

if __name__ == "__main__":
    generate()
