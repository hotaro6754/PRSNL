# Volume 5: Machine Learning in Cyber

## Chapter 41: Deterministic vs Probabilistic Defense
A deterministic rule says: `IF ports_scanned > 500 THEN alert`. It is 100% accurate but easily evaded (the attacker simply scans 499 ports). 
A probabilistic (ML) model says: `This behavior looks 94% similar to a botnet`. It catches unknown attacks but suffers from False Positives. PS26145 uses both.

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
$$ H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i) $$
High entropy means high chaos. Benign networks have low entropy.

## Chapter 46: XGBoost in PS26145
We chose **eXtreme Gradient Boosting (XGBoost)** for V5.
* **Speed**: C++ core, processes inferences in 1.40ms.
* **Accuracy**: 99.34% F1 Score.
* **Explainability**: Decision trees allow us to trace exactly *why* a flow was marked malicious.

## Chapter 47: Evidence Fusion
An ML model's output is just a probability. Our Fusion Engine combines the XGBoost score with deterministic rule triggers (e.g., a known bad SNI certificate) to synthesize a final `SecurityCase`.
