# Feature Engineering and Mathematics

Feature engineering transforms raw logs into numerical values that XGBoost and deterministic rules can understand.

## Inter-Arrival Time (IAT)
The time between consecutive packets in a flow.
$$
IAT_i = t_i - t_{i-1}
$$

* **Why it matters**: Botnet C2 beaconing has very low variance in IAT (highly periodic).

## Shannon Entropy
Measures the randomness of a string.
$$
H(X) = -\sum p(x) \log_2 p(x)
$$

* **Why it matters**: DGA (Domain Generation Algorithms) domains like `q9x3vj8.com` have high entropy compared to `google.com`.

## Exfiltration Asymmetry
$$
Ratio = \frac{Outbound\ Bytes}{Inbound\ Bytes}
$$

* **Why it matters**: Standard web traffic pulls more data down than it sends up. If a host sends 1400x more data up than it receives down, it is likely exfiltrating data.

```text
Inbound   █
Outbound  ███████████████████████████
Detector: exfil_v1
```