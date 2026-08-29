import pandas as pd
from typing import List, Dict, Tuple
from urllib.parse import urlparse
import logging

logger = logging.getLogger('DataQuality')

def normalize_url_schema(df: pd.DataFrame, url_col: str = 'url', label_col: str = 'label') -> pd.DataFrame:
    """Normalizes the schema for URL datasets to have 'url' and 'label' columns."""
    if url_col not in df.columns or label_col not in df.columns:
        raise ValueError(f"Missing required columns {url_col} or {label_col}")
    
    df_normalized = df[[url_col, label_col]].copy()
    df_normalized.columns = ['text', 'label']  # 'text' for generic content
    df_normalized['type'] = 'url'
    return df_normalized

def deduplicate(df: pd.DataFrame, subset: List[str] = ['text']) -> pd.DataFrame:
    """Removes duplicate rows based on subset."""
    initial_len = len(df)
    df_dedup = df.drop_duplicates(subset=subset).copy()
    logger.info(f"Deduplication removed {initial_len - len(df_dedup)} records")
    return df_dedup

def extract_domain(url: str) -> str:
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        return urlparse(url).netloc
    except Exception:
        return ""

def domain_family_holdout_split(df: pd.DataFrame, test_ratio: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Splits dataset ensuring domains are held out to prevent data leakage."""
    if 'text' not in df.columns or df['type'].iloc[0] != 'url':
        # Default random split if not URL
        from sklearn.model_selection import train_test_split
        train, test = train_test_split(df, test_size=test_ratio, random_state=42)
        return train, test

    df['domain'] = df['text'].apply(extract_domain)
    domains = df['domain'].unique()
    
    import numpy as np
    np.random.seed(42)
    np.random.shuffle(domains)
    
    split_idx = int(len(domains) * (1 - test_ratio))
    train_domains = set(domains[:split_idx])
    
    train_df = df[df['domain'].isin(train_domains)].drop(columns=['domain'])
    test_df = df[~df['domain'].isin(train_domains)].drop(columns=['domain'])
    
    logger.info(f"Domain holdout split: {len(train_df)} train, {len(test_df)} test records")
    return train_df, test_df
