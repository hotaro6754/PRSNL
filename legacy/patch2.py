with open('backend/ml/router.py', 'r') as f:
    content = f.read()

import re

# Add loading of the new models
new_load = '''        # --- Supervised model (RETIRED) ---
        self.xgb_model = None

        # --- Isolation Forest anomaly model (RETIRED) ---
        self.iforest_model = None

        # --- New Windowed Models ---
        xgb_path_v2 = os.path.join(self.model_dir, "xgb_window_v2_shadow.pkl")
        xgb_meta_path_v2 = os.path.join(self.model_dir, "xgb_window_v2_metadata.json")
        if os.path.exists(xgb_path_v2):
            try:
                import joblib
                self.xgb_model = joblib.load(xgb_path_v2)
                if os.path.exists(xgb_meta_path_v2):
                    with open(xgb_meta_path_v2) as f:
                        self.xgb_metadata = json.load(f)
                logger.info("Loaded XGBoost model %s (version %s)", self.xgb_metadata.get("model_id"), self.xgb_metadata.get("version"))
            except Exception as e:
                logger.error("Failed to load xgb_window_v2: %s", e)
                
        iforest_path_v2 = os.path.join(self.model_dir, "iforest_window_v2_shadow.pkl")
        iforest_meta_path_v2 = os.path.join(self.model_dir, "iforest_window_v2_metadata.json")
        if os.path.exists(iforest_path_v2):
            try:
                import joblib
                self.iforest_model = joblib.load(iforest_path_v2)
                if os.path.exists(iforest_meta_path_v2):
                    with open(iforest_meta_path_v2) as f:
                        self.iforest_metadata = json.load(f)
                logger.info("Loaded Isolation Forest window_v2 model")
            except Exception as e:
                logger.error("Failed to load iforest_window_v2: %s", e)'''

content = re.sub(r'        # --- Supervised model \(RETIRED\).*?self\.iforest_model = None', new_load, content, flags=re.DOTALL)

with open('backend/ml/router.py', 'w') as f:
    f.write(content)
