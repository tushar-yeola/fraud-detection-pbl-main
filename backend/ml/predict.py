import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), 'artifacts')

_rf_model = None
_lr_model = None
_scaler = None
_encoders = None
_metrics = None
_feature_names = None


def _load_artifacts():
    global _rf_model, _lr_model, _scaler, _encoders, _metrics, _feature_names
    import json
    _rf_model = joblib.load(os.path.join(ARTIFACTS_DIR, 'rf_model.pkl'))
    _lr_model = joblib.load(os.path.join(ARTIFACTS_DIR, 'lr_model.pkl'))
    _scaler = joblib.load(os.path.join(ARTIFACTS_DIR, 'scaler.pkl'))
    _encoders = joblib.load(os.path.join(ARTIFACTS_DIR, 'encoders.pkl'))
    with open(os.path.join(ARTIFACTS_DIR, 'metrics.json')) as f:
        _metrics = json.load(f)
    _feature_names = _metrics['feature_names']


def get_metrics():
    if _metrics is None:
        _load_artifacts()
    return _metrics


def predict_transaction(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict fraud probability for a single transaction dict.
    raw: dict with keys matching original CSV column names (before preprocessing).
    Returns: {'is_fraud': bool, 'fraud_probability': float, 'risk_level': str, 'fraud_reasons': list}
    """
    if _rf_model is None:
        _load_artifacts()

    df = pd.DataFrame([raw])

    # Drop ID columns
    drop_cols = ['TransactionID', 'AccountID', 'DeviceID', 'MerchantID', 'IP Address']
    df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

    # Parse dates
    for c in df.columns:
        if 'date' in c.lower() or 'time' in c.lower():
            try:
                df[c] = pd.to_datetime(df[c], errors='coerce')
            except Exception:
                pass

    # Feature engineering
    if 'TransactionDate' in df.columns:
        df['hour'] = df['TransactionDate'].dt.hour
        df['day_of_week'] = df['TransactionDate'].dt.dayofweek
        df['month'] = df['TransactionDate'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(int)

    if 'TransactionDate' in df.columns and 'PreviousTransactionDate' in df.columns:
        df['days_since_last_txn'] = (
            df['TransactionDate'] - df['PreviousTransactionDate']
        ).dt.total_seconds() / 86400
        df['days_since_last_txn'] = df['days_since_last_txn'].fillna(999).clip(-1, 365)

    # Drop raw date cols
    date_cols = [c for c in df.columns if hasattr(df[c], 'dt')]
    df.drop(columns=date_cols, inplace=True)

    # Encode categoricals
    for c, le in _encoders.items():
        if c in df.columns:
            val = str(df[c].iloc[0])
            if val in le.classes_:
                df[c] = le.transform([val])
            else:
                df[c] = len(le.classes_)  # unknown category

    # Align features
    for f in _feature_names:
        if f not in df.columns:
            df[f] = 0
    df = df[_feature_names]
    df.fillna(0, inplace=True)

    # RF prediction (no scaling)
    rf_proba = float(_rf_model.predict_proba(df)[0][1])
    # LR prediction (scaled)
    df_sc = _scaler.transform(df)
    lr_proba = float(_lr_model.predict_proba(df_sc)[0][1])

    # Ensemble: average both models
    best = _metrics.get('best_model', 'random_forest')
    if best == 'random_forest':
        fraud_prob = 0.7 * rf_proba + 0.3 * lr_proba
    else:
        fraud_prob = 0.3 * rf_proba + 0.7 * lr_proba

    is_fraud = fraud_prob >= 0.5
    if fraud_prob >= 0.75:
        risk = 'HIGH'
    elif fraud_prob >= 0.4:
        risk = 'MEDIUM'
    else:
        risk = 'LOW'

    # Generate reasons based on thresholds
    reasons = []
    if raw.get('TransactionAmount', 0) > 2500:
        reasons.append(f"Unusually high transaction amount (${raw.get('TransactionAmount')})")
    
    if raw.get('LoginAttempts', 0) > 3:
        reasons.append(f"Multiple consecutive failed login attempts ({raw.get('LoginAttempts')})")
        
    try:
        tx_dt = pd.to_datetime(raw.get('TransactionDate'))
        if tx_dt.hour >= 23 or tx_dt.hour <= 4:
            reasons.append("Transaction occurred during unusual late-night hours")
    except:
        pass
        
    try:
        if raw.get('PreviousTransactionDate'):
            prev_dt = pd.to_datetime(raw.get('PreviousTransactionDate'))
            if (pd.to_datetime(raw.get('TransactionDate')) - prev_dt).total_seconds() < 60:
                reasons.append("Ultra-fast successive transactions detected (< 60s)")
    except:
        pass
        
    if fraud_prob >= 0.6 and not reasons:
        reasons.append("Model detected anomalous behavioral patterns (Ensemble Alert)")

    return {
        'is_fraud': bool(is_fraud),
        'fraud_probability': round(fraud_prob, 4),
        'rf_probability': round(rf_proba, 4),
        'lr_probability': round(lr_proba, 4),
        'risk_level': risk,
        'fraud_reasons': reasons,
    }
