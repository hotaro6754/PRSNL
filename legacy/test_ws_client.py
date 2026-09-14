import asyncio
import websockets
import requests
import json

async def test_websocket_flow():
    uri = "ws://127.0.0.1:8000/alerts"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket.")
            
            # Trigger replay via HTTP
            print("Triggering Replay API...")
            res = requests.post("http://127.0.0.1:8000/replay", json={"filename": "data/pcaps/real_port_scan.pcap"})
            print(f"Replay API Response: {res.json()}")
            
            # Wait for alerts
            print("Waiting for alerts on WebSocket...")
            for i in range(2): # We expect 2 alerts (PortScan and Beaconing from M0)
                message = await websocket.recv()
                alert = json.loads(message)
                print(f"RECEIVED WS ALERT: {alert['threat_class']} | Confidence: {alert['confidence']}")
                print(f"EVIDENCE: {alert['evidence']}")
                
            print("Successfully verified WebSocket flow.")
            
    except Exception as e:
        print(f"Error during WS test: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_flow())
