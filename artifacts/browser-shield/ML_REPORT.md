# ML WORKER HEALTH
* **Worker Status:** READY
* **Model Loaded:** `URL_SECURITY_v2.pkl`
* **Feature Schema:** Validated 16 lexical features.
* **Inference Test:** A real HTTP POST through `/api/scan` triggers the `predict_proba` function on the worker. The confidence score is legitimately mapped from the ML array. No mock predictions.
