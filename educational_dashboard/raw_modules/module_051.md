# Module 051: Hardware Diodes
## 1. What is it? (Explain from scratch for a complete beginner)
No software is 100% hack-proof. For the most highly classified networks (like nuclear power plants), we use a **Hardware Diode** (or Data Diode).
A diode is a physical piece of networking hardware that allows data to flow in **only one direction**. It physically has a transmitter (laser) on one side and a receiver (sensor) on the other, but no cable going back. Because of physics, it is physically impossible for a hacker on the outside to send data *into* the protected network.

## 2. Architecture / Logic
```mermaid

flowchart LR
    A["Highly Secure Network"] -->|Fiber Optic TX| B((Data Diode))
    B -->|Fiber Optic RX| C["Outside World / Monitoring"]
    C -.->|PHYSICALLY IMPOSSIBLE| B
```

## 3. Implementation
While a real diode is hardware, here is how you simulate one-way UDP communication in Python.

```python
import socket

def simulate_diode_tx(data):
    # Transmitter (TX) - Sends data, but NEVER listens for a response
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Send data to the outside network
    sock.sendto(data.encode(), ("192.168.1.100", 5005))
    print("TX: Data sent out. No acknowledgment required.")
    # No sock.recv() exists here.

def simulate_diode_rx():
    # Receiver (RX) - Listens for data, but NEVER sends data back
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 5005))
    print("RX: Listening for inbound data...")
    # data, addr = sock.recvfrom(1024)
    # print("RX: Received data:", data)
    # No sock.send() exists here.

simulate_diode_tx("System Health: OK")
```

## 4. Line-by-Line Explanation
- `socket.SOCK_DGRAM`: We use UDP. Unlike TCP, UDP does not require a "handshake" or two-way communication. It just blasts data into the void.
- `simulate_diode_tx`: The secure network sends data out. Notice there is absolutely no code to receive data. In a real diode, the receiving wire is physically cut.
- `simulate_diode_rx`: The outside monitoring system listens. It cannot talk back because it physically lacks a transmitting laser.

## 5. Summary
Hardware Diodes enforce absolute, physics-based network segmentation. They allow a secure system to push logs, alerts, or backups to the outside world for monitoring, while making it physically impossible for an external attacker to send malicious commands back in.
