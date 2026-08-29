# Ask the Jury Questions

**Q: Why passive?**
A: To guarantee the security tool cannot be weaponized against the production enclave.

**Q: Why XGBoost instead of Deep Learning?**
A: Network metadata is tabular. XGBoost is faster, highly accurate, and explainable, whereas Deep Learning is overkill for structured tabular arrays.

**Q: Why did V4 fail?**
A: Scapy (training) and Zeek (production) parsed network bytes differently (L2 vs L3). The semantic mismatch broke the model.

**Q: How do you detect encrypted traffic?**
A: We DO NOT decrypt. We use TLS metadata (JA3 fingerprints) combined with behavioral flow metrics (bytes, timing, directionality).