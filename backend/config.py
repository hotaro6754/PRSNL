import os
from enum import Enum

class ThreatClass(str, Enum):
    """Enumeration of possible threat classes."""
    DDoS = "DDoS"
    Beaconing = "Beaconing"
    DGA = "DGA"
    Tunneling = "Tunneling"
    TLSAnomaly = "TLSAnomaly"
    PortScan = "PortScan"
    Exfiltration = "Exfiltration"
    SlowHTTP = "SlowHTTP"
    BruteForce = "BruteForce"

class Severity(str, Enum):
    """Enumeration of alert severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class AppEnv(str, Enum):
    PRODUCTION = "PRODUCTION"
    SHADOW = "SHADOW"
    EVALUATION = "EVALUATION"
    LAB = "LAB"
    TEST = "TEST"

# Current environment
ENVIRONMENT = AppEnv(os.getenv("APP_ENV", "LAB").upper())

# ML Stage determines if ML generates independent alerts or is shadow-only
ML_STAGE = AppEnv(os.getenv("ML_STAGE", "SHADOW").upper())

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCAP_DIR = os.path.join(BASE_DIR, "pcaps")
MODEL_DIR = os.path.join(BASE_DIR, "models")
BUFFER_DIR = os.path.join(BASE_DIR, "data", "buffers")
os.makedirs(BUFFER_DIR, exist_ok=True)
