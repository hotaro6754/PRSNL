import os

OUTPUT_DIR = r"E:\cyberos-prototype\cyberos-docs\docs\handbook"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def write_file(filename, content):
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# ==========================================
# VOLUME 5: MACHINE LEARNING IN CYBER
# ==========================================
VOL5_CONTENT = """
# Volume 5: Machine Learning in Cyber

## Chapter 41: Deterministic vs Probabilistic Defense
A deterministic rule says: `IF ports_scanned > 500 THEN alert`. It is 100% accurate but easily evaded (the attacker simply scans 499 ports). 
A probabilistic (ML) model says: `This behavior looks 94% similar to a botnet`. It catches unknown attacks but suffers from False Positives. CyberOS uses both.

## Chapter 42: Machine Learning Basics
Machine learning algorithmically derives patterns from historical data. 
1. **Features**: The measurable variables (e.g., bytes, duration).
2. **Labels**: Ground truth (0 = Benign, 1 = Malicious).
3. **Training**: The algorithm fits a mathematical boundary between the classes.

## Chapter 43: Tabular Data Supremacy
Network flow logs (like Zeek `conn.log`) are structured tabular data (rows and columns). While Deep Learning (Neural Networks) dominates unstructured data (images, text), Gradient Boosted Trees dominate tabular data.

## Chapter 44: Feature Engineering
Raw IP addresses cannot be fed to an ML model. We must engineer numerical features.
* **Inter-Arrival Time (IAT)**: Time between packets. Highly periodic IAT indicates C2 beaconing.
* **Exfiltration Asymmetry**: Ratio of outbound to inbound bytes.

## Chapter 45: Entropy and Mathematics
To detect DGA (Domain Generation Algorithms) and IP spoofing, we calculate Shannon Entropy.
$$ H(X) = -\\sum_{i=1}^{n} P(x_i) \\log_2 P(x_i) $$
High entropy means high chaos. Benign networks have low entropy.

## Chapter 46: XGBoost in CyberOS
We chose **eXtreme Gradient Boosting (XGBoost)** for V5.
* **Speed**: C++ core, processes inferences in 1.40ms.
* **Accuracy**: 99.34% F1 Score.
* **Explainability**: Decision trees allow us to trace exactly *why* a flow was marked malicious.

## Chapter 47: Evidence Fusion
An ML model's output is just a probability. Our Fusion Engine combines the XGBoost score with deterministic rule triggers (e.g., a known bad SNI certificate) to synthesize a final `SecurityCase`.
"""

# ==========================================
# VOLUME 6: VALIDATION & OPERATIONS
# ==========================================
VOL6_CONTENT = """
# Volume 6: Validation, Deployment & Future

## Chapter 48: The T1-T15 Requirements Matrix
CyberOS was rigorously tested against 15 specific network conditions (T1 to T15). 
These ranged from simple ping sweeps (T10) to encrypted C2 tunneling (T9) and volumetric spoofing (T15).

## Chapter 49: True Positives (11/12)
The V5 architecture successfully detected 11 out of the 12 malicious attack vectors in the live stream container environment, achieving a 1.000 Precision rate and 0.000 FPR.

## Chapter 50: The T11 False Negative
We do not hide failures. The system failed to detect T11 (Slow Port Scan). Because the attacker deliberately spaced their scans 30 seconds apart, the behavior was fractured across multiple 10-second tumbling windows. The system reset its counters before the threshold was met.

## Chapter 51: Hardware Diodes
Software cannot guarantee unidirectional data flow. If a server is compromised, the software can be rewritten. The final deployment requires a physical Hardware Data Diode—a fiber optic cable with the return wire physically cut.

## Chapter 52: Model Governance
How do we update the ML model without breaking production?
1. **Shadow Mode**: The new model runs alongside V5 but its alerts are hidden.
2. **Evaluation**: We compare Shadow alerts to V5 alerts.
3. **Canary**: We route 5% of traffic to the new model.
4. **Production**: 100% rollout.

## Chapter 53: The Final Verdict
CyberOS demonstrates that a purely passive, metadata-driven NDR system can achieve 99.3% accuracy without decrypting payloads. The integration of deterministic rules with XGBoost streaming analytics provides a robust, scalable defense mechanism for critical infrastructure.
"""

def generate():
    write_file("05_volume_5.md", VOL5_CONTENT)
    write_file("06_volume_6.md", VOL6_CONTENT)
    print("Volumes 5 and 6 (Chapters 41-53) generated successfully.")

if __name__ == "__main__":
    generate()
