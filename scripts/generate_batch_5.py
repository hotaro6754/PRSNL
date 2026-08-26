import os

def write_module(mod_id, content):
    filepath = rf"E:\sih26145-prototype\educational_dashboard\raw_modules\module_{mod_id}.md"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

content_41 = """# Module 041: Deterministic vs Probabilistic Defense
## 1. What is it? (Explain from scratch for a complete beginner)
In cybersecurity, we have two main ways to catch bad guys: **Deterministic** and **Probabilistic** defense. 
- **Deterministic Defense** is like a bouncer at a club with a strict VIP list. If your name is on the "bad guys" list (like a known malware signature or a bad IP address), you are blocked. It uses strict *rules*.
- **Probabilistic Defense** is like a seasoned detective. It doesn't just look for known bad names; it looks at *behavior*. If someone is sweating, wearing a ski mask, and carrying a crowbar, the detective calculates a *probability* that this person is up to no good, even if they've never been seen before. This relies on Machine Learning (ML).

## 2. Architecture / Logic
```mermaid
flowchart TD
    A[Incoming Network Traffic] --> B{Defense Type}
    B -->|Deterministic| C[Check Signature Database]
    C -->|Match Found| D[Block]
    C -->|No Match| E[Allow]
    B -->|Probabilistic| F[Machine Learning Model]
    F -->|Probability > 90%| D
    F -->|Probability < 90%| E
```

## 3. Implementation
```python
def deterministic_defense(ip_address):
    bad_ips = ["192.168.1.50", "10.0.0.99"]
    if ip_address in bad_ips:
        return "Blocked by Rule"
    return "Allowed"

def probabilistic_defense(ml_model, traffic_features):
    # Predict the probability of being malicious
    malicious_probability = ml_model.predict_proba(traffic_features)[0][1]
    if malicious_probability > 0.85:
        return f"Blocked by ML (Confidence: {malicious_probability*100}%)"
    return "Allowed"
```

## 4. Line-by-Line Explanation
- `bad_ips = [...]`: We define a hardcoded list of known threats for deterministic defense.
- `if ip_address in bad_ips`: This is the strict rule. It either matches exactly, or it doesn't.
- `malicious_probability = ml_model.predict_proba(traffic_features)[0][1]`: Here, an ML model looks at the traffic's features and outputs a percentage (probability) of it being an attack.
- `if malicious_probability > 0.85`: Instead of an exact match, we use a threshold (85%). If the model is confident enough, we block it.

## 5. Summary
Deterministic defense is highly accurate for *known* threats but fails against new, unseen attacks (zero-days). Probabilistic defense uses AI to guess if something is bad based on its behavior, allowing us to catch brand-new attacks, though it occasionally makes mistakes (false positives).
"""

content_42 = """# Module 042: Machine Learning Basics (Features & Labels)
## 1. What is it? (Explain from scratch for a complete beginner)
When we teach a computer to find malware using Machine Learning, we have to speak its language. We do this using **Features** and **Labels**.
- **Features** are the characteristics or clues. Imagine you are trying to guess if an animal is a dog or a cat. The features would be: *Weight, Ear Shape, Barking (Yes/No)*. In cybersecurity, features are things like: *File Size, Network Port, Number of failed logins*.
- **Labels** are the answers. It's what we are trying to predict. In our animal example, the label is "Dog" or "Cat". In cybersecurity, the label is usually "Malicious" or "Benign" (safe).

## 2. Architecture / Logic
```mermaid
flowchart LR
    A[Raw Data: Network Packet] --> B[Feature Extraction]
    B --> C[Feature 1: Packet Size]
    B --> D[Feature 2: Destination Port]
    B --> E[Feature 3: Protocol]
    C --> F[Machine Learning Algorithm]
    D --> F
    E --> F
    F --> G[Label: Malicious or Benign]
```

## 3. Implementation
```python
import pandas as pd

# Creating a dataset of network traffic
data = {
    'Packet_Size': [500, 1500, 64, 9000],          # Feature 1
    'Dest_Port': [80, 443, 22, 4444],              # Feature 2
    'Failed_Logins': [0, 0, 5, 0],                 # Feature 3
    'Label': ['Benign', 'Benign', 'Malicious', 'Malicious'] # The Answer
}

df = pd.DataFrame(data)

# Separating Features (X) and Labels (y)
X_features = df[['Packet_Size', 'Dest_Port', 'Failed_Logins']]
y_labels = df['Label']

print("Features (Clues):\\n", X_features)
print("\\nLabels (Answers):\\n", y_labels)
```

## 4. Line-by-Line Explanation
- `data = {...}`: We create a dictionary containing our columns. Three columns are our features, and one is our label.
- `pd.DataFrame(data)`: We convert this dictionary into a Pandas DataFrame, which is basically a virtual Excel spreadsheet.
- `X_features = df[['Packet_Size', 'Dest_Port', 'Failed_Logins']]`: We create a new variable `X` that holds *only* the clues.
- `y_labels = df['Label']`: We create a variable `y` that holds *only* the answers.

## 5. Summary
To do machine learning, we need historical data. We extract measurable properties called **Features** (the X variables) and pair them with the correct answers called **Labels** (the y variable). The ML algorithm studies the relationship between the features and the labels so it can predict labels for new data.
"""

content_43 = """# Module 043: Tabular Data Supremacy in InfoSec
## 1. What is it? (Explain from scratch for a complete beginner)
When you hear about Artificial Intelligence, you often hear about Deep Learning (Neural Networks) doing amazing things like recognizing faces or writing essays. But in Cybersecurity (InfoSec), standard **Tabular Data** models (like Random Forests and XGBoost) usually beat Deep Learning!
Tabular data is just data that fits nicely into rows and columns, like a CSV file or an Excel spreadsheet. Network logs, firewall events, and user logins are naturally tabular. Standard ML models are faster, use less memory, and are often much more accurate for this specific type of data than massive deep neural networks.

## 2. Architecture / Logic
```mermaid
flowchart TD
    A[Security Logs / NetFlow] --> B[Structured CSV/Database]
    B --> C{Which ML Model?}
    C -->|Deep Learning| D[Requires massive compute, slow, often overfits]
    C -->|Tree-based Models XGBoost| E[Fast, highly accurate, explainable]
    E --> F[Winner for InfoSec!]
```

## 3. Implementation
```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Loading tabular InfoSec data (rows and columns)
tabular_data = pd.DataFrame({
    'bytes_sent': [450, 89000, 120, 5000000],
    'duration_sec': [1, 5, 0.1, 3600],
    'is_malware': [0, 1, 0, 1]
})

X = tabular_data[['bytes_sent', 'duration_sec']]
y = tabular_data['is_malware']

# Using a standard Tree-based model (supreme for tabular data)
model = RandomForestClassifier(n_estimators=10)
model.fit(X, y)

print("Model trained successfully on tabular data!")
```

## 4. Line-by-Line Explanation
- `tabular_data = pd.DataFrame(...)`: We create structured, row-and-column data representing network sessions.
- `X = ...` and `y = ...`: We split the tabular data into our features (bytes sent, duration) and our label (is_malware).
- `RandomForestClassifier(n_estimators=10)`: We initialize a Random Forest, which is a classic tabular data model made of multiple decision trees.
- `model.fit(X, y)`: The model learns the patterns in the spreadsheet instantly, without the need for complex, heavy Deep Learning mathematics.

## 5. Summary
While Neural Networks are great for images and text, InfoSec data is mostly tabular (logs, flows, events). For tabular data, tree-based algorithms like XGBoost and Random Forest are supreme because they are faster, require less tuning, and provide excellent accuracy.
"""

content_44 = """# Module 044: Feature Engineering for Network Flows
## 1. What is it? (Explain from scratch for a complete beginner)
A network flow is just a record of a conversation between two computers (e.g., Computer A talked to Computer B for 5 minutes and sent 100 packets). But raw flows aren't always useful for AI. 
**Feature Engineering** is the art of taking raw data and doing math on it to create *better, smarter clues* (features) for our Machine Learning model. For example, instead of just giving the model "Total Bytes" and "Total Time", we can engineer a new feature: "Bytes per Second". This new feature might immediately expose a data exfiltration attack!

## 2. Architecture / Logic
```mermaid
flowchart LR
    A[Raw Flow Data] --> B(Bytes: 5000, Time: 5s)
    B --> C{Feature Engineering}
    C --> D[Feature: Bytes/Sec = 1000]
    C --> E[Feature: Packets/Sec = 20]
    D --> F[ML Model]
    E --> F
```

## 3. Implementation
```python
import pandas as pd

# Raw Network Flow Data
flows = pd.DataFrame({
    'source_ip': ['10.0.0.1', '10.0.0.2'],
    'total_bytes': [15000, 8000000],
    'total_packets': [15, 8000],
    'duration_seconds': [5, 2]
})

# --- Feature Engineering ---
# 1. Calculate Bytes per Second
flows['bytes_per_sec'] = flows['total_bytes'] / flows['duration_seconds']

# 2. Calculate Average Packet Size
flows['avg_packet_size'] = flows['total_bytes'] / flows['total_packets']

print("Engineered Features:\\n", flows[['bytes_per_sec', 'avg_packet_size']])
```

## 4. Line-by-Line Explanation
- `flows = pd.DataFrame(...)`: We start with raw, un-optimized data directly from our network router or firewall.
- `flows['bytes_per_sec'] = ...`: We create a brand new column. We divide `total_bytes` by `duration_seconds`. If this number is extremely high, it might indicate a file download or data theft.
- `flows['avg_packet_size'] = ...`: We create another feature. If average packet size is very small, it might be a ping sweep or port scan.

## 5. Summary
Feature Engineering is the most important step in Machine Learning. By mathematically combining and transforming raw network data into meaningful metrics (like rates, averages, and ratios), we make it much easier for the AI to spot malicious behavior.
"""

content_45 = """# Module 045: Entropy and Mathematics in Detection
## 1. What is it? (Explain from scratch for a complete beginner)
How can you tell if a file contains plain text or if it's an encrypted ransomware payload? You can use **Entropy**!
In cybersecurity, entropy is a mathematical measurement of *randomness* or *chaos* in a piece of data. 
- Normal English text has low entropy (predictable letters, lots of spaces).
- Encrypted data or compressed malware has very **high entropy** (looks completely random).
By measuring the entropy of network packets or files, we can mathematically detect if someone is trying to hide malicious code.

## 2. Architecture / Logic
The formula for Shannon Entropy (H) is:
$$ H(X) = - \sum_{i=1}^{n} P(x_i) \log_2 P(x_i) $$
Where $P(x_i)$ is the probability (frequency) of a specific byte appearing in the data.

```mermaid
flowchart TD
    A[Incoming File / Payload] --> B[Calculate Byte Frequencies]
    B --> C[Apply Shannon Entropy Formula]
    C --> D{Entropy Score (0 to 8)}
    D -->|> 7.5| E[High Chaos: Likely Encrypted / Malware!]
    D -->|< 6.0| F[Low Chaos: Plaintext / Normal Data]
```

## 3. Implementation
```python
import math
from collections import Counter

def calculate_entropy(data_string):
    # Count how many times each character appears
    frequencies = Counter(data_string)
    length = len(data_string)
    
    entropy = 0.0
    for count in frequencies.values():
        probability = count / length
        # Shannon Entropy math
        entropy -= probability * math.log2(probability)
        
    return entropy

# Test cases
normal_text = "Hello world, this is a normal sentence."
encrypted_malware = "x8f\\x9a\\x02\\x1b\\x7f\\xa3\\xcc\\x4d\\xe1\\x55\\x89"

print(f"Normal text entropy: {calculate_entropy(normal_text):.2f}")
print(f"Encrypted malware entropy: {calculate_entropy(encrypted_malware):.2f}")
```

## 4. Line-by-Line Explanation
- `Counter(data_string)`: This counts the occurrences of every single byte/character in the data.
- `probability = count / length`: We find the percentage chance of any given byte appearing.
- `entropy -= probability * math.log2(probability)`: This is the Shannon Entropy formula. It sums up the unpredictability of every byte.
- When applied to `normal_text`, the score is low (around 3.0 - 4.0) because letters like 'e' and ' ' (space) are predictable. The `encrypted_malware` scores much higher because every byte is totally random.

## 5. Summary
Entropy is a powerful mathematical tool in cybersecurity. By calculating how "random" a file or network payload is, defenders can easily spot encrypted communication, packed malware, or ransomware without needing to know the actual contents of the file.
"""

content_46 = """# Module 046: eXtreme Gradient Boosting (XGBoost)
## 1. What is it? (Explain from scratch for a complete beginner)
**XGBoost** stands for eXtreme Gradient Boosting. It is one of the most powerful Machine Learning algorithms in the world for tabular data.
Imagine you have a team of detectives. The first detective looks at the evidence and makes a guess, but makes some mistakes. The second detective looks *only* at the mistakes the first one made and tries to fix them. The third looks at the second's mistakes, and so on. 
XGBoost builds hundreds of small Decision Trees in a sequence, where each new tree specifically tries to correct the errors of the previous trees.

## 2. Architecture / Logic
```mermaid
flowchart LR
    A[Input Data] --> B[Tree 1: Makes a guess]
    B --> C[Calculate Errors/Residuals]
    C --> D[Tree 2: Learns to fix Tree 1's errors]
    D --> E[Calculate Errors]
    E --> F[Tree 3: Learns to fix Tree 2's errors]
    F --> G[Final XGBoost Prediction]
```

## 3. Implementation
```python
import xgboost as xgb
import numpy as np

# Feature 1: Payload size, Feature 2: Entropy
X_train = np.array([[500, 3.2], [1500, 7.9], [64, 2.1], [8000, 7.8]])
# 0 = Benign, 1 = Malware
y_train = np.array([0, 1, 0, 1]) 

# Initialize the XGBoost Classifier
model = xgb.XGBClassifier(n_estimators=10, learning_rate=0.1)

# Train the model (Building the sequential trees)
model.fit(X_train, y_train)

# Test with a new network flow (Size=7500, Entropy=7.95)
new_flow = np.array([[7500, 7.95]])
prediction = model.predict(new_flow)

print("Prediction (0=Safe, 1=Malware):", prediction[0])
```

## 4. Line-by-Line Explanation
- `import xgboost as xgb`: We import the XGBoost library.
- `X_train` and `y_train`: We set up some dummy training data. Notice how malware (1) has high entropy.
- `xgb.XGBClassifier(n_estimators=10, learning_rate=0.1)`: We create the model. `n_estimators=10` means it will build 10 trees in a sequence. `learning_rate` controls how aggressively each tree corrects the last one.
- `model.fit(X_train, y_train)`: The algorithm trains, building trees step-by-step to minimize prediction error.
- `model.predict(new_flow)`: We ask the fully trained team of trees to classify a new, unseen network packet.

## 5. Summary
XGBoost is an ensemble learning method that uses sequential decision trees. Because it explicitly focuses on correcting its own past mistakes, it achieves incredibly high accuracy and is a favorite algorithm for cybersecurity data scientists detecting anomalies in network traffic.
"""

content_47 = """# Module 047: Evidence Fusion Engine
## 1. What is it? (Explain from scratch for a complete beginner)
In a real Security Operations Center (SOC), you don't rely on just one tool. You might have an Antivirus, a Firewall, an Intrusion Detection System (IDS), and a Machine Learning model. 
An **Evidence Fusion Engine** is a central brain that takes the alerts (evidence) from all these different tools and mathematically fuses them together to make one final, highly accurate decision. It weighs the evidence based on how much it trusts each tool.

## 2. Architecture / Logic
```mermaid
flowchart TD
    A[ML Model Score: 70% bad] --> D[Evidence Fusion Engine]
    B[Firewall Rule: Port 4444 open] --> D
    C[Threat Intel: IP is suspicious] --> D
    D --> E{Weighted Calculation}
    E -->|> Threshold| F[Trigger Critical Alert]
    E -->|< Threshold| G[Log as Low Priority]
```

## 3. Implementation
```python
def fusion_engine(ml_score, rule_matched, intel_flagged):
    # Weights define how much we trust each source
    weight_ml = 0.4
    weight_rule = 0.3
    weight_intel = 0.3
    
    # Normalize inputs to 0.0 or 1.0 (except ML which is already a probability)
    rule_score = 1.0 if rule_matched else 0.0
    intel_score = 1.0 if intel_flagged else 0.0
    
    # Calculate fused confidence score
    fused_score = (ml_score * weight_ml) + (rule_score * weight_rule) + (intel_score * weight_intel)
    
    print(f"Fused Threat Score: {fused_score:.2f}")
    
    if fused_score > 0.75:
        return "CRITICAL ALERT: Isolate Machine"
    return "MONITOR: Not enough evidence"

# Scenario: ML is suspicious, Rule didn't trigger, Threat Intel knows the IP is bad
action = fusion_engine(ml_score=0.85, rule_matched=False, intel_flagged=True)
print("Action Taken:", action)
```

## 4. Line-by-Line Explanation
- `weight_... = ...`: We assign weights. If they add up to 1.0 (100%), it forms a weighted average.
- `rule_score = 1.0 if rule_matched else 0.0`: We convert Boolean (True/False) alerts into numbers so we can do math on them.
- `fused_score = (ml_score * weight_ml) + ...`: The Fusion Engine multiplies each piece of evidence by its weight and adds them up.
- `if fused_score > 0.75:`: We only isolate the machine if the combined evidence crosses a high threshold, preventing false alarms.

## 5. Summary
An Evidence Fusion Engine solves the problem of "alert fatigue." By combining multiple weak signals (a slightly suspicious ML score, a generic threat intel flag) using weighted math, it creates a single, high-confidence alert that security analysts can actually trust.
"""

content_48 = """# Module 048: The T1-T15 Requirements Matrix
## 1. What is it? (Explain from scratch for a complete beginner)
When building a security architecture, you can't just guess if you are secure. The **T1-T15 Requirements Matrix** (a conceptual framework similar to MITRE ATT&CK or strict compliance frameworks) is a checklist of 15 critical technical requirements your defense system must meet. 
These requirements range from T1 (Must inspect all inbound traffic) to T15 (Must have zero physical connection to the outside world - hardware diodes). Using a matrix ensures there are no blind spots in your defense grid.

## 2. Architecture / Logic
```mermaid
flowchart LR
    A[Security Architecture] --> B[T1: Packet Inspection]
    A --> C[T5: Machine Learning Validation]
    A --> D[T11: Evasion Prevention]
    A --> E[T15: Hardware Diode Isolation]
    B --> F[Matrix Compliant]
    C --> F
    D --> F
    E --> F
```

## 3. Implementation
```python
# A dictionary representing the T1-T15 validation matrix
compliance_matrix = {
    "T1_Packet_Inspection": True,
    "T5_ML_Detection": True,
    "T11_Evasion_Protection": False, # Uh oh, we are failing this requirement!
    "T15_Physical_Isolation": True
}

def validate_architecture(matrix):
    failed_controls = []
    for requirement, status in matrix.items():
        if status == False:
            failed_controls.append(requirement)
            
    if failed_controls:
        print(f"SYSTEM NON-COMPLIANT. Fix the following: {failed_controls}")
    else:
        print("System fully meets the T1-T15 Requirements Matrix.")

validate_architecture(compliance_matrix)
```

## 4. Line-by-Line Explanation
- `compliance_matrix = {...}`: We define a JSON-like structure that tracks whether our network meets the specific technical requirements (T1 through T15).
- `for requirement, status in matrix.items():`: We loop through every requirement in the matrix.
- `if status == False:`: We check if any requirement is currently failing.
- `failed_controls.append(requirement)`: If it's failing, we add it to a list of violations that the security engineering team needs to fix immediately.

## 5. Summary
The T1-T15 Requirements Matrix is an engineering blueprint. It turns abstract security concepts into a strict, auditable checklist, ensuring that systems possess layered defenses, ML capabilities, and physical safeguards without leaving dangerous gaps.
"""

content_49 = """# Module 049: True Positives and Model Precision
## 1. What is it? (Explain from scratch for a complete beginner)
When evaluating an ML model, we can't just ask "Is it accurate?" We need to be specific. 
- **True Positive (TP):** The model caught actual malware. (YAY!)
- **False Positive (FP):** The model flagged a normal file as malware. (Annoying for users!)
- **Precision** is a specific math formula: Out of everything the model *claimed* was malware, what percentage was *actually* malware? If precision is low, your security team will waste all day investigating False Positives.

## 2. Architecture / Logic
$$ Precision = \\frac{True Positives}{True Positives + False Positives} $$

```mermaid
pie title Model Alerts (Precision = 80%)
    "True Positives (Actual Malware)" : 80
    "False Positives (Wrong Alarms)" : 20
```

## 3. Implementation
```python
from sklearn.metrics import precision_score, confusion_matrix

# True answers (1 = Malware, 0 = Safe)
actual_reality = [1, 0, 0, 1, 1, 0]

# What our ML model guessed
model_guesses  = [1, 1, 0, 1, 0, 0]

# Calculate Precision
# The model guessed Malware for indices 0, 1, 3. 
# Actual reality for those indices is 1, 0, 1.
# So it got 2 True Positives, and 1 False Positive (index 1).
precision = precision_score(actual_reality, model_guesses)

# Extract TP and FP
tn, fp, fn, tp = confusion_matrix(actual_reality, model_guesses).ravel()

print(f"True Positives: {tp}")
print(f"False Positives: {fp}")
print(f"Model Precision: {precision * 100:.1f}%")
```

## 4. Line-by-Line Explanation
- `actual_reality`: This is the ground truth. We have 3 malware files and 3 safe files.
- `model_guesses`: The model guessed that the first, second, and fourth files were malware. 
- Notice the second file: Reality was `0`, but the model guessed `1`. That is a **False Positive**.
- `precision_score(...)`: This calculates the math for us. The model yelled "Malware!" 3 times. 2 times it was right (TP), 1 time it was wrong (FP). Precision = 2 / (2 + 1) = 66.7%.

## 5. Summary
In cybersecurity, Precision is critical. A model with low precision generates too many False Positives (alert fatigue). By tracking True Positives vs False Positives, engineers can tune their XGBoost models to only flag traffic when they are absolutely certain.
"""

content_50 = """# Module 050: The T11 False Negative (Evasion)
## 1. What is it? (Explain from scratch for a complete beginner)
A **False Negative (FN)** is the worst-case scenario in cybersecurity: Malware enters the network, and the security model says "Looks safe to me!" (Negative).
In the T11 requirement, we specifically worry about **Evasion Attacks** (Adversarial ML). This is when a hacker purposefully slightly alters their malware (like adding a few blank bytes) so that it still does damage, but the Machine Learning model's math gets confused and misclassifies it as benign.

## 2. Architecture / Logic
```mermaid
flowchart LR
    A[Malware Payload] --> B[Adversarial Evasion Tool]
    B --> C[Altered Payload with Junk Data]
    C --> D[ML Classifier]
    D --> E[Prediction: Benign!]
    E --> F[False Negative: Network Breached]
```

## 3. Implementation
```python
# Simulating an Evasion Attack on a basic ML check
def simple_ml_model(payload_size_bytes):
    # Model learned that payloads over 1000 bytes are usually safe (like images)
    if payload_size_bytes > 1000:
        return "Benign (Safe)"
    else:
        return "Malware!"

# Hacker's original malware is small (500 bytes)
original_malware_size = 500
print("Original Attack:", simple_ml_model(original_malware_size)) # Caught!

# Hacker evades detection by padding malware with 600 bytes of zeros
evasion_padding = 600
altered_malware_size = original_malware_size + evasion_padding

print("Evasion Attack:", simple_ml_model(altered_malware_size)) # False Negative!
```

## 4. Line-by-Line Explanation
- `simple_ml_model(payload_size_bytes)`: Imagine a highly simplified ML model that thinks small files are exploits and large files are safe documents.
- The `original_malware_size` is 500 bytes. The model successfully flags it as "Malware!"
- `evasion_padding = 600`: The attacker figures out the model's blind spot. They add 600 bytes of useless data (zeros) to their malware.
- The `altered_malware_size` is now 1100 bytes. The model outputs "Benign". This is a **False Negative** caused by evasion.

## 5. Summary
Machine Learning is not bulletproof. Hackers use evasion techniques (Adversarial AI) to manipulate features—like changing file sizes, adjusting entropy, or spoofing ports—to trick models into generating False Negatives. Defenders must constantly retrain models on adversarial examples to satisfy requirement T11.
"""

content_51 = """# Module 051: Hardware Diodes
## 1. What is it? (Explain from scratch for a complete beginner)
No software is 100% hack-proof. For the most highly classified networks (like nuclear power plants), we use a **Hardware Diode** (or Data Diode).
A diode is a physical piece of networking hardware that allows data to flow in **only one direction**. It physically has a transmitter (laser) on one side and a receiver (sensor) on the other, but no cable going back. Because of physics, it is physically impossible for a hacker on the outside to send data *into* the protected network.

## 2. Architecture / Logic
```mermaid
flowchart LR
    A[Highly Secure Network] -->|Fiber Optic TX| B((Data Diode))
    B -->|Fiber Optic RX| C[Outside World / Monitoring]
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
"""

content_52 = """# Module 052: Model Governance & Shadow Mode
## 1. What is it? (Explain from scratch for a complete beginner)
If you train a new ML model to block hackers, you can't just plug it into your network and turn it on immediately. What if it accidentally blocks the CEO's laptop? 
**Model Governance** is the process of safely deploying AI. We use **Shadow Mode** (also called Dark Launching). The new model runs live on real network traffic and makes predictions, but it is *muted*. It only writes its predictions to a log file. Security engineers analyze the logs to ensure it's safe before giving it the power to actually block traffic.

## 2. Architecture / Logic
```mermaid
flowchart TD
    A[Live Network Traffic] --> B[Current System - Rules]
    B --> C[Action: Block or Allow]
    A --> D[New ML Model in Shadow Mode]
    D --> E[Log Prediction to Database ONLY]
    E -.->|Engineers Review Logs| F[Promote to Active?]
```

## 3. Implementation
```python
def active_defense(traffic):
    # Standard rule-based firewall
    return "Allowed by Firewall"

def shadow_mode_model(traffic, is_active=False):
    # The new Machine Learning model
    prediction = "Block (Malware detected!)"
    
    if is_active:
        # If fully deployed, actually take action
        return prediction
    else:
        # SHADOW MODE: Just log it, don't interfere
        print(f"[SHADOW LOG] Model would have done: {prediction}")
        return None

# Processing a network packet
packet = "Normal Web Browsing"

# The active system processes traffic normally
firewall_action = active_defense(packet)
print("Actual Action Taken:", firewall_action)

# The new model evaluates the same traffic silently
shadow_mode_model(packet, is_active=False)
```

## 4. Line-by-Line Explanation
- `active_defense()`: The current legacy system is the only thing allowed to actually interact with the traffic.
- `is_active=False`: By default, our new ML model is placed in Shadow Mode.
- `if is_active:`: This is the governance switch. It prevents the ML model from returning a block command.
- `print("[SHADOW LOG]...")`: Instead of blocking, it simply logs what it *would* have done. Engineers can review this later to check for False Positives.

## 5. Summary
Model Governance and Shadow Mode prevent catastrophic AI failures in production. By allowing a new ML model to evaluate live traffic without the authority to take action, defenders can safely validate its precision and recall in the real world before flipping the switch to "Active."
"""

content_53 = """# Module 053: The Final Verdict
## 1. What is it? (Explain from scratch for a complete beginner)
**The Final Verdict** is the ultimate output of the entire cybersecurity pipeline. 
Traffic entered the network, features were engineered, XGBoost analyzed it, the Evidence Fusion Engine weighed the scores, and it passed Shadow Mode. Now, the system must make an automated, irreversible decision: *Allow*, *Alert*, or *Isolate*. The Final Verdict is where data science turns into kinetic network action.

## 2. Architecture / Logic
```mermaid
flowchart TD
    A[Evidence Fusion Score] --> B{Threshold Check}
    B -->|< 50%| C[VERDICT: Allow Traffic]
    B -->|50% - 85%| D[VERDICT: Send Alert to SOC]
    B -->|> 85%| E[VERDICT: API Call to Isolate Host]
    E --> F[Network Port Disabled]
```

## 3. Implementation
```python
import requests

def execute_final_verdict(fusion_score, host_ip):
    print(f"--- Evaluating Final Verdict for {host_ip} ---")
    
    if fusion_score < 0.50:
        print("Verdict: ALLOW. Traffic is benign.")
        
    elif 0.50 <= fusion_score < 0.85:
        print("Verdict: ALERT. Creating ticket for SOC Analyst.")
        # Trigger an email or Slack alert here
        
    else:
        print("Verdict: ISOLATE. Critical threat detected!")
        # Simulate an API call to a Cisco/Palo Alto switch to kill the port
        api_payload = {"ip": host_ip, "action": "quarantine"}
        print(f"[API CALL] Sent to Network Controller: {api_payload}")
        return "Host Isolated"

# Simulating the end of the pipeline
execute_final_verdict(fusion_score=0.92, host_ip="10.0.5.50")
```

## 4. Line-by-Line Explanation
- `execute_final_verdict(...)`: The function that takes the final mathematical score from the fusion engine.
- `if fusion_score < 0.50:`: Low scores are allowed through immediately. Minimal latency.
- `elif ... < 0.85:`: Medium scores generate alerts. The system isn't confident enough to break the user's connection, so it asks a human to look.
- `else:`: High scores (>85%) trigger automated response.
- `api_payload = ...`: The python script actually reaches out to network hardware (like a firewall or switch) via an API to physically disconnect the infected machine.

## 5. Summary
The Final Verdict is the culmination of Deterministic and Probabilistic defense. It takes the mathematical certainty of the ML models and translates it into automated, decisive action to protect the network. It proves that ML in InfoSec is not just about logging alerts—it is about active, automated defense.
"""

write_module("041", content_41)
write_module("042", content_42)
write_module("043", content_43)
write_module("044", content_44)
write_module("045", content_45)
write_module("046", content_46)
write_module("047", content_47)
write_module("048", content_48)
write_module("049", content_49)
write_module("050", content_50)
write_module("051", content_51)
write_module("052", content_52)
write_module("053", content_53)

print("Generated 13 markdown modules successfully.")
