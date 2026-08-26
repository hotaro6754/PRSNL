import re

with open('backend/ml/router.py', 'r') as f:
    content = f.read()

# Update the load_models method to load v3
new_load = '''        try:
            self.xgb_model = joblib.load(os.path.join(model_dir, "xgb_window_v3_shadow.pkl"))
            with open(os.path.join(model_dir, "xgb_window_v3_metadata.json")) as f:
                self.xgb_meta = json.load(f)
                
            self.iforest_model = joblib.load(os.path.join(model_dir, "iforest_window_v3_shadow.pkl"))
            with open(os.path.join(model_dir, "iforest_window_v3_metadata.json")) as f:
                self.iforest_meta = json.load(f)
                
            self.stage = "SHADOW"
            logger.info(f"Loaded Shadow Models: {self.xgb_meta['model_id']} & {self.iforest_meta['model_id']}")
            
        except Exception as e:
            logger.error(f"Failed to load shadow models: {e}")'''

content = re.sub(r'        try:\n            self\.xgb_model = joblib\.load\(os\.path\.join\(model_dir, "xgb_window_v2_shadow\.pkl"\)\).*?logger\.error\(f"Failed to load shadow models: \{e\}"\)', new_load, content, flags=re.DOTALL)

with open('backend/ml/router.py', 'w') as f:
    f.write(content)
