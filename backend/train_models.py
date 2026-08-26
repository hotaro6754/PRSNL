import os
import pickle
import numpy as np
from sklearn.ensemble import IsolationForest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def train_ddos_model():
    logger.info("Generating synthetic training data for DDoS model...")
    # Using raw numpy arrays instead of pandas to avoid Windows build dependencies
    # Features: [pps, bps, unique_src_ips, syn_like_count, src_ip_entropy, flow_count]
    normal_data = np.column_stack((
        np.random.normal(50, 10, 1000),
        np.random.normal(50000, 10000, 1000),
        np.random.randint(10, 100, 1000),
        np.random.randint(0, 5, 1000),
        np.random.uniform(3.0, 5.0, 1000),
        np.random.randint(10, 150, 1000)
    ))
    
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(normal_data)
    
    model_path = os.path.join(MODELS_DIR, "ddos_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"DDoS model saved to {model_path}")

def train_dga_model():
    logger.info("Generating synthetic training data for DGA model...")
    # Features: [total_length, sld_length, sld_entropy, numeric_ratio, consonant_ratio]
    normal_data = np.column_stack((
        np.random.normal(15, 3, 1000),
        np.random.normal(10, 2, 1000),
        np.random.uniform(1.5, 2.5, 1000),
        np.random.uniform(0.0, 0.1, 1000),
        np.random.uniform(0.4, 0.6, 1000)
    ))
    
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(normal_data)
    
    model_path = os.path.join(MODELS_DIR, "dga_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"DGA model saved to {model_path}")

if __name__ == "__main__":
    train_ddos_model()
    train_dga_model()
    logger.info("Model training completed successfully.")
