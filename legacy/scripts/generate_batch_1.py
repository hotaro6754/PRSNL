import os

modules = [
    {
        "id": "001",
        "title": "What is a Network? (OSI vs TCP/IP)",
        "content": """# Module 001: What is a Network? (OSI vs TCP/IP)

## 1. What is it? (Explain from scratch for a complete beginner)
Imagine a network as a postal system, but for computers. When you write a letter to a friend, you put it in an envelope, write the address on it, and hand it over to the post office. The post office then figures out the best way to get that letter to your friend's house, whether it's via a truck, plane, or local mail carrier. 
In the digital world, a **Network** is simply two or more computers connected together so they can share information, just like the postal system shares letters. The internet itself is just one massive, global network of networks!
To make sure every computer understands each other (like speaking the same language), they use special rules called **Protocols**. The two most famous frameworks for understanding these rules are the **OSI Model** (a theoretical 7-layer concept) and the **TCP/IP Model** (a practical 4-layer model used on the internet today).

## 2. System Architecture / Flow (MUST include a Mermaid flowchart/sequence diagram)
```mermaid
flowchart TD
    subgraph OSI Model
        A1[Layer 7: Application]
        A2[Layer 6: Presentation]
        A3[Layer 5: Session]
        A4[Layer 4: Transport]
        A5[Layer 3: Network]
        A6[Layer 2: Data Link]
        A7[Layer 1: Physical]
    end
    
    subgraph TCP/IP Model
        B1[Application Layer]
        B4[Transport Layer]
        B5[Internet Layer]
        B6[Network Access Layer]
    end
    
    A1 & A2 & A3 --> B1
    A4 --> B4
    A5 --> B5
    A6 & A7 --> B6
```

## 3. Implementation / Configuration (Include Python/CLI examples)
To see your computer's connection in a network, you can use built-in command-line tools.
**Windows Command Prompt:**
```cmd
ipconfig
```
**Linux/macOS Terminal:**
```bash
ifconfig
# or modern alternative
ip a
```

## 4. Line-by-Line Explanation
- `ipconfig`: This Windows command stands for "Internet Protocol Configuration". When you run it, your computer asks the operating system to print out the current network settings.
- `ifconfig`: This is the older Linux/macOS equivalent (Interface Configuration).
- `ip a`: The modern Linux command to show IP addresses. It lists all network interfaces (like Wi-Fi or Ethernet) and the addresses assigned to them, showing how you are connected to the network.

## 5. Summary
A network connects computers to share data using standard protocols. The OSI model describes how networks work theoretically using 7 layers, while TCP/IP is the practical 4-layer model used by the internet today. You can check your own network connection using commands like `ipconfig` or `ip a`.
"""
    },
    {
        "id": "002",
        "title": "Packets, Frames, and Bits",
        "content": """# Module 002: Packets, Frames, and Bits

## 1. What is it? (Explain from scratch for a complete beginner)
When you send a large file like a photo over the internet, it doesn't travel as one giant block. That would easily clog up the network! Instead, the photo is chopped up into tiny, manageable pieces. 
These pieces have different names depending on where they are in the network process:
- **Bits:** The smallest unit of data, represented as 1s and 0s. This is how data physically travels over cables (as electrical pulses) or Wi-Fi (as radio waves).
- **Frames:** When bits are grouped together on a local network (like your home Wi-Fi), they are called a Frame. Frames contain physical addresses (MAC addresses) so computers on the same network can find each other.
- **Packets:** When a frame needs to leave your home network and travel across the internet, it is wrapped in an IP (Internet Protocol) address. This wrapped data is called a Packet. Think of a packet as an envelope with a global address on it!

## 2. System Architecture / Flow (MUST include a Mermaid flowchart/sequence diagram)
```mermaid
flowchart LR
    A[Data 'Photo'] --> B(Segment/Datagram)
    B --> C(Packet<br/>IP Addresses Added)
    C --> D(Frame<br/>MAC Addresses Added)
    D --> E((Bits<br/>1010101 sent over wire))
```

## 3. Implementation / Configuration (Include Python/CLI examples)
You can see packets flowing through your network by sending small test packets to another computer using the `ping` command.
**CLI Command (Windows/Linux/macOS):**
```bash
ping google.com -c 4
```

## 4. Line-by-Line Explanation
- `ping`: The command used to test if another computer is reachable across a network. It sends a special type of packet called an ICMP Echo Request.
- `google.com`: The destination we are sending our packets to.
- `-c 4`: This flag tells the command to send exactly 4 packets (Count = 4). (Note: On Windows, use `-n 4`).
- Output: The terminal will show each packet as it returns from Google, displaying how long it took in milliseconds. If the packet gets lost, it will say "Request timed out".

## 5. Summary
Data travels across networks by being broken down. The smallest unit is a Bit (1s and 0s), which forms Frames for local networks, and Packets for global internet travel. The `ping` command is a simple way to test if your packets are successfully reaching their destination.
"""
    },
    {
        "id": "003",
        "title": "IP Addresses and Subnetting",
        "content": """# Module 003: IP Addresses and Subnetting

## 1. What is it? (Explain from scratch for a complete beginner)
Just as every house needs a mailing address for the postman to deliver letters, every computer connected to a network needs an address so other computers can send it data. This is called an **IP Address** (Internet Protocol Address).
An IPv4 address looks like four numbers separated by dots, like `192.168.1.10`.
**Subnetting** is a way of dividing a large network into smaller, more efficient networks (called subnets). Imagine a large city divided into zip codes. If a post office only had to deliver mail to a specific zip code rather than the entire city, it would be much faster. Subnetting does exactly this for computer networks, keeping traffic localized and secure.

## 2. System Architecture / Flow (MUST include a Mermaid flowchart/sequence diagram)
```mermaid
flowchart TD
    A[Main Network: 192.168.1.0/24]
    A --> B[Router]
    B --> C(Subnet A: 192.168.1.1 to .127)
    B --> D(Subnet B: 192.168.1.128 to .255)
    
    C --> E[PC 1: 192.168.1.10]
    C --> F[PC 2: 192.168.1.20]
    
    D --> G[Server 1: 192.168.1.150]
```

## 3. Implementation / Configuration (Include Python/CLI examples)
Python has a great built-in library for calculating IP addresses and subnets.
**Python Script:**
```python
import ipaddress

network = ipaddress.ip_network('192.168.1.0/24')
print(f"Total IPs in network: {network.num_addresses}")
print(f"First usable IP: {network[1]}")
print(f"Subnet Mask: {network.netmask}")
```

## 4. Line-by-Line Explanation
- `import ipaddress`: Imports Python's built-in module specifically designed for inspecting and manipulating IP addresses.
- `ip_network('192.168.1.0/24')`: We define a network. The `/24` tells us the size of the subnet mask, which dictates how many addresses belong to this network.
- `network.num_addresses`: Calculates the total number of IP addresses available in this specific subnet (in a /24, it's 256).
- `network[1]`: Grabs the first usable IP address in the network (often assigned to the router).
- `network.netmask`: Displays the subnet mask (which would be 255.255.255.0), the mechanism used to separate the network portion from the host portion of the address.

## 5. Summary
IP addresses are the unique identifiers for devices on a network. Subnetting allows us to break large networks down into smaller, manageable, and more secure segments. We can use tools like Python's `ipaddress` module to easily calculate network sizes and available IPs.
"""
    },
    {
        "id": "004",
        "title": "The TCP 3-Way Handshake",
        "content": """# Module 004: The TCP 3-Way Handshake

## 1. What is it? (Explain from scratch for a complete beginner)
Imagine you want to make a phone call. Before you can start talking, you dial the number, wait for the other person to say "Hello?", and then you say "Hi, it's me!". Only after this polite introduction do you begin your conversation.
Computers use a very similar polite introduction when they want to send data reliably. This process is called the **TCP 3-Way Handshake**. 
TCP (Transmission Control Protocol) is a set of rules that ensures data arrives perfectly, without missing any pieces. To guarantee this, the two computers must first agree to a connection using three steps:
1. **SYN (Synchronize):** Computer A says, "Hello, can we talk?"
2. **SYN-ACK (Synchronize-Acknowledge):** Computer B replies, "Yes, I hear you, we can talk!"
3. **ACK (Acknowledge):** Computer A says, "Great, I'm starting to send data now."

## 2. System Architecture / Flow (MUST include a Mermaid flowchart/sequence diagram)
```mermaid
sequenceDiagram
    participant Client
    participant Server
    Client->>Server: 1. SYN (Hello, can we connect?)
    Server-->>Client: 2. SYN-ACK (Yes, I hear you! Ready?)
    Client->>Server: 3. ACK (Got it. Here comes the data!)
    Note over Client,Server: Connection Established
    Client->>Server: Data Transfer begins...
```

## 3. Implementation / Configuration (Include Python/CLI examples)
We can create a simple TCP connection in Python using sockets to trigger this handshake.
**Python Script:**
```python
import socket

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# This single line triggers the 3-Way Handshake!
client_socket.connect(("google.com", 80))

print("Handshake successful, connected to Google on port 80!")
client_socket.close()
```

## 4. Line-by-Line Explanation
- `import socket`: Brings in the Python module used for network connections.
- `socket.socket(...)`: Creates a new "socket", which is basically a software plug. `AF_INET` means we are using IPv4 addresses, and `SOCK_STREAM` means we specifically want to use TCP (which requires the handshake).
- `client_socket.connect(...)`: This is where the magic happens. By calling `connect`, your computer automatically sends the SYN packet to `google.com` on port 80 (web traffic). Google responds with SYN-ACK, and your computer automatically replies with ACK.
- `print(...)`: Confirms that the 3-way handshake completed without any errors.
- `client_socket.close()`: Politely closes the connection when we are done.

## 5. Summary
The TCP 3-Way Handshake is a reliable introduction protocol (SYN, SYN-ACK, ACK) that two computers perform before sending data to ensure both sides are ready and listening. This reliability makes TCP the backbone of the internet for things like loading web pages and downloading files.
"""
    },
    {
        "id": "005",
        "title": "UDP: The Best Effort Protocol",
        "content": """# Module 005: UDP: The Best Effort Protocol

## 1. What is it? (Explain from scratch for a complete beginner)
If TCP is like a registered mail service where you get a signature confirming delivery, **UDP** (User Datagram Protocol) is like throwing a postcard out of a moving car window towards someone's mailbox. You hope it gets there, but you don't stick around to check!
UDP is a "connectionless" protocol. It doesn't use the polite TCP 3-way handshake. It just starts blasting data at the destination immediately. 
Why would we want a protocol that might lose data? **Speed!** Because UDP skips the handshakes and the delivery confirmations, it is incredibly fast. It's used for things where a missing packet doesn't ruin the whole experience, like live video streaming (a dropped frame just causes a brief glitch), online gaming (you want the newest location data instantly), or Voice over IP phone calls.

## 2. System Architecture / Flow (MUST include a Mermaid flowchart/sequence diagram)
```mermaid
sequenceDiagram
    participant Client
    participant Server
    Note over Client,Server: No Handshake!
    Client->>Server: Data Packet 1
    Client->>Server: Data Packet 2
    Client--xServer: Data Packet 3 (LOST in transit)
    Client->>Server: Data Packet 4
    Note over Server: Server receives 1, 2, and 4. It does not ask for 3 again.
```

## 3. Implementation / Configuration (Include Python/CLI examples)
Creating a UDP connection in Python is very simple since there is no connection setup phase.
**Python Script:**
```python
import socket

# Create a UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Message to send
message = b"Hello Server, catching this?"

# Blast the data immediately without connect()
udp_socket.sendto(message, ("127.0.0.1", 9999))
print("Message sent via UDP!")
```

## 4. Line-by-Line Explanation
- `socket.socket(...)`: Creates the network plug. This time we use `SOCK_DGRAM`, which tells Python we want to use UDP instead of TCP.
- `message = b"..."`: The `b` converts the text into bytes, which is the raw format data needs to be in to travel over a network.
- `udp_socket.sendto(...)`: Notice we didn't use `connect()`! We use `sendto()` to simply aim the data at an IP (`127.0.0.1`, which is local loopback) and a port (`9999`), and fire it off immediately. There is no check to see if anyone is listening on port 9999.
- `print(...)`: Confirms our code executed.

## 5. Summary
UDP is a fast, connectionless protocol that sacrifices reliability for speed. It is perfect for real-time applications like video games and live streaming where getting data instantly is more important than getting every single piece perfectly.
"""
    },
    {
        "id": "006",
        "title": "Ports and Sockets",
        "content": """# Module 006: Ports and Sockets

## 1. What is it? (Explain from scratch for a complete beginner)
Imagine an IP address is an apartment building. A package (packet) arrives at the building because it has the correct street address (IP address). But how does the postman know *which* apartment door to deliver it to? That's where **Ports** come in!
A Port is simply an apartment number for a computer. When data arrives at your computer's IP address, the Port number tells the computer which specific application should receive that data. 
- Port 80 goes to the Web Server application.
- Port 25 goes to the Email application.
A **Socket** is the combination of an IP Address and a Port number (e.g., `192.168.1.10:80`). It represents a single, complete destination for data.

## 2. System Architecture / Flow (MUST include a Mermaid flowchart/sequence diagram)
```mermaid
flowchart LR
    A[Incoming Packet] --> B[IP Address: 192.168.1.50]
    B --> C{Which Port?}
    C -- Port 80 --> D[Web Browser Application]
    C -- Port 22 --> E[SSH/Terminal Application]
    C -- Port 443 --> F[Secure Web Browser]
```

## 3. Implementation / Configuration (Include Python/CLI examples)
You can see which ports are currently open and listening on your computer using the command line.
**CLI Command (Windows/Linux/macOS):**
```bash
netstat -an
```

## 4. Line-by-Line Explanation
- `netstat`: Network Statistics. This is a classic command-line tool used to display active network connections and listening ports.
- `-a`: Displays **A**ll active connections and listening ports on your machine.
- `-n`: Displays addresses and port numbers in **N**umerical form, rather than trying to look up the names (which makes the command run much faster).
- The output will show columns for Protocol (TCP/UDP), Local Address (your IP and Port, e.g., 127.0.0.1:443), and the State of the connection (e.g., LISTENING, ESTABLISHED).

## 5. Summary
While an IP Address gets data to the right computer, a Port gets data to the right application on that computer. A Socket is the combination of an IP and a Port, forming a complete digital address. You can view your computer's open ports using tools like `netstat`.
"""
    },
    {
        "id": "007",
        "title": "DNS: The Phonebook of the Internet",
        "content": """# Module 007: DNS: The Phonebook of the Internet

## 1. What is it? (Explain from scratch for a complete beginner)
Computers communicate using IP Addresses (like `142.250.190.46`). However, humans are terrible at remembering random strings of numbers! We prefer names like `google.com` or `amazon.com`. 
To solve this problem, we created the **Domain Name System (DNS)**. DNS is literally the phonebook of the internet. When you type `google.com` into your browser, your computer secretly asks a DNS server, "Hey, what is the IP address for google.com?" The DNS server looks up the name, finds the number `142.250.190.46`, and hands it back to your computer so it can make the connection.

## 2. System Architecture / Flow (MUST include a Mermaid flowchart/sequence diagram)
```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant DNSServer as DNS Server
    participant WebServer as Web Server
    
    User->>Browser: Types "google.com"
    Browser->>DNSServer: DNS Query: What is the IP for google.com?
    DNSServer-->>Browser: DNS Response: 142.250.190.46
    Browser->>WebServer: TCP Connection to 142.250.190.46
    WebServer-->>Browser: Sends Webpage content
```

## 3. Implementation / Configuration (Include Python/CLI examples)
You can act as your own computer and ask DNS servers for IP addresses using the `nslookup` or `dig` commands.
**CLI Command (Windows/Linux/macOS):**
```bash
nslookup google.com
```

**Python Script:**
```python
import socket

# Ask the OS to resolve a hostname to an IP
ip_address = socket.gethostbyname("geeksforgeeks.org")
print(f"The IP address is: {ip_address}")
```

## 4. Line-by-Line Explanation
**Python:**
- `import socket`: The network library.
- `socket.gethostbyname(...)`: This function triggers a DNS lookup. It takes a human-readable domain name string and queries your computer's configured DNS server.
- The returned value is the numerical IP address, which is then printed to the screen.

**CLI:**
- `nslookup`: Stands for Name Server Lookup. It asks the DNS server for the IP record associated with the domain name provided.

## 5. Summary
DNS translates human-readable domain names (like website URLs) into computer-readable IP addresses. Without DNS, we would have to memorize a string of numbers for every website we wanted to visit. Tools like `nslookup` or Python's `socket` library allow us to perform these translations manually.
"""
    },
    {
        "id": "008",
        "title": "HTTP and The Web",
        "content": """# Module 008: HTTP and The Web

## 1. What is it? (Explain from scratch for a complete beginner)
When you browse the web, your browser and the website's server are talking to each other using a language called **HTTP** (HyperText Transfer Protocol). 
Think of HTTP like placing an order at a restaurant. 
1. **The Request:** You (the client) look at the menu and tell the waiter, "I want a burger." (An HTTP GET request).
2. **The Response:** The waiter goes to the kitchen (the server), gets your food, and brings it back to you on a plate (An HTTP Response with the webpage data).
HTTP requests usually contain a "Method" indicating what you want to do: `GET` (give me a webpage) or `POST` (I am sending you data, like a login form).

## 2. System Architecture / Flow (MUST include a Mermaid flowchart/sequence diagram)
```mermaid
sequenceDiagram
    participant Client as Web Browser
    participant Server as Web Server
    
    Client->>Server: HTTP GET /index.html
    Note over Server: Server finds the file
    Server-->>Client: HTTP 200 OK + HTML Content
    
    Client->>Server: HTTP POST /login (username/password)
    Note over Server: Server checks credentials
    Server-->>Client: HTTP 302 Found (Redirect to Dashboard)
```

## 3. Implementation / Configuration (Include Python/CLI examples)
Python's `requests` library is the easiest way to speak HTTP through code.
**Python Script:**
```python
import requests

# Send an HTTP GET request to a website
response = requests.get("https://httpbin.org/get")

# Check the HTTP Status Code (200 means OK)
print(f"Status Code: {response.status_code}")

# Print the text content returned by the server
print("Response Data:")
print(response.text)
```

## 4. Line-by-Line Explanation
- `import requests`: Imports a highly popular, third-party Python library for making HTTP requests (you may need to install it via `pip install requests`).
- `requests.get(...)`: Creates and sends an HTTP GET request to the URL provided. The server's reply is saved into the `response` variable.
- `response.status_code`: Every HTTP response comes with a number. `200` means success. `404` means not found. `500` means server error.
- `response.text`: This extracts the actual body of the response (the HTML text, or in this case, JSON data) so we can read it.

## 5. Summary
HTTP is the language of the World Wide Web. It operates on a simple Request and Response cycle between a client (your browser) and a server. Using methods like GET and POST, and checking Status Codes like 200 or 404, we can interact with web servers easily using tools like Python's `requests` library.
"""
    },
    {
        "id": "009",
        "title": "Encryption, TLS, and SSL",
        "content": """# Module 009: Encryption, TLS, and SSL

## 1. What is it? (Explain from scratch for a complete beginner)
If standard HTTP is like sending a postcard through the mail (anyone handling it can read what it says), **HTTPS** (the S stands for Secure) is like putting that postcard inside a locked steel box.
To lock the box, we use **Encryption**, which scrambles the data so it looks like gibberish to anyone who doesn't have the secret key to unlock it. 
**TLS (Transport Layer Security)**, and its older predecessor **SSL**, are the protocols that provide this encryption for the web. When you see a little padlock icon next to a URL in your browser, it means a TLS handshake occurred, secret keys were exchanged securely, and all your web traffic is now scrambled and safe from eavesdroppers.

## 2. System Architecture / Flow (MUST include a Mermaid flowchart/sequence diagram)
```mermaid
sequenceDiagram
    participant Browser
    participant Server
    
    Browser->>Server: ClientHello (Let's connect securely!)
    Server-->>Browser: ServerHello & Digital Certificate
    Note over Browser: Browser verifies the Certificate
    Browser->>Server: Session Key Exchange (Encrypted)
    Note over Browser,Server: Secure TLS Tunnel Established
    Browser->>Server: Encrypted HTTP GET Request
    Server-->>Browser: Encrypted HTTP Response
```

## 3. Implementation / Configuration (Include Python/CLI examples)
We can use Python to inspect the TLS certificate of a website to see if it is secure.
**Python Script:**
```python
import ssl
import socket

hostname = 'www.google.com'
context = ssl.create_default_context()

with socket.create_connection((hostname, 443)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(f"TLS Version: {ssock.version()}")
        cert = ssock.getpeercert()
        print(f"Issued To: {cert['subject'][0][0][1]}")
```

## 4. Line-by-Line Explanation
- `import ssl`: Imports Python's built-in module for TLS/SSL encryption.
- `ssl.create_default_context()`: Sets up the default security settings (trusted certificate authorities, secure cipher suites).
- `socket.create_connection(...)`: Opens a standard TCP connection to port 443 (the default port for secure HTTPS traffic).
- `context.wrap_socket(...)`: This is the crucial step. It takes our plain TCP connection and "wraps" it in TLS encryption, performing the secure handshake.
- `ssock.version()`: Prints the version of TLS being used (e.g., TLSv1.3).
- `ssock.getpeercert()`: Downloads the digital certificate from the server so we can see who it was issued to.

## 5. Summary
Encryption protects data from being read by unauthorized people. TLS (and SSL) provides a secure, encrypted tunnel for web traffic, upgrading insecure HTTP to secure HTTPS. This process ensures that passwords and sensitive data are safe as they travel across the internet.
"""
    },
    {
        "id": "010",
        "title": "Packets vs. Flows (Crucial for NDR)",
        "content": """# Module 010: Packets vs. Flows (Crucial for NDR)

## 1. What is it? (Explain from scratch for a complete beginner)
In the world of Cybersecurity, specifically **NDR** (Network Detection and Response), security analysts have to monitor network traffic for hackers. They do this in two main ways: looking at **Packets** or looking at **Flows**.
- **Packet Capture (PCAP):** This is like recording the complete audio of a phone call. You capture every single byte of data sent. It is highly detailed but takes up a massive amount of hard drive space and is hard to search quickly.
- **Network Flows (NetFlow/IPFIX):** This is like looking at a phone bill. It doesn't record the audio of the call, but it tells you *who* called *whom*, at what *time*, and for *how long*. It is metadata. Flows are tiny, easy to store for months, and perfect for spotting weird trends (like a computer suddenly uploading gigabytes of data to an unknown country at 3 AM).

## 2. System Architecture / Flow (MUST include a Mermaid flowchart/sequence diagram)
```mermaid
flowchart TD
    A[Network Traffic] --> B{Security Sensor}
    B -- Full PCAP --> C[(Massive Storage Array)]
    B -- Flow Metadata --> D[(Small Database)]
    
    C --> E[Deep Forensic Analysis<br/>(Slow but exact)]
    D --> F[Trend & Anomaly Detection<br/>(Fast and lightweight)]
```

## 3. Implementation / Configuration (Include Python/CLI examples)
While Python code for flow generation is complex, here is how you might capture packets vs view flows conceptually on a Linux CLI.
**Capture Packets (Heavy):**
```bash
tcpdump -w traffic.pcap -i eth0
```
*`tcpdump` grabs the entire packet (headers + data body) on interface `eth0` and writes it to a file. This file will grow extremely fast.*

**Analyze Flows (Lightweight, via a tool like Zeek):**
```bash
cat conn.log | awk '{print $3, $5, $9}'
```
*A flow log (like Zeek's `conn.log`) already summarizes the data. This `awk` command easily extracts just the Source IP, Destination IP, and Bytes Transferred without needing to read heavy packet data.*

## 4. Line-by-Line Explanation
- `tcpdump -w traffic.pcap -i eth0`: `tcpdump` is the packet capture tool. `-w` means write to file, and `-i eth0` specifies which network card to listen on.
- `cat conn.log`: Reads out the connection flow log generated by a sensor.
- `awk '{print $3, $5, $9}'`: Awk is a text-processing tool. Here, it is pulling out the 3rd, 5th, and 9th columns of the log (which typically correspond to Source IP, Destination IP, and Bytes).

## 5. Summary
For network security, we must choose between detail and efficiency. Packets (PCAP) contain the full payload of data, useful for deep forensic investigations but expensive to store. Network Flows contain lightweight metadata (source, destination, time, size), which is ideal for long-term storage and detecting anomalous behavior using NDR tools.
"""
    }
]

def main():
    base_dir = r"E:\cyberos-prototype\educational_dashboard\raw_modules"
    os.makedirs(base_dir, exist_ok=True)
    
    for mod in modules:
        filename = f"module_{mod['id']}.md"
        filepath = os.path.join(base_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(mod['content'])
        print(f"Generated {filepath}")

if __name__ == '__main__':
    main()
