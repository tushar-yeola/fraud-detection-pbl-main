import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, roc_auc_score, confusion_matrix,
    precision_score, recall_score, f1_score, average_precision_score
)
from imblearn.over_sampling import SMOTE
import joblib
import json
import os
import warnings
warnings.filterwarnings('ignore')

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'transactions.csv')
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), 'artifacts')
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def generate_fraud_labels(df: pd.DataFrame) -> pd.Series:
    """
    Generate IsFraud labels using banking domain heuristics.
    High score → more likely fraud. Threshold at top ~10%.
    """
    score = np.zeros(len(df))

    # High login attempts (>= 3 is suspicious)
    if 'LoginAttempts' in df.columns:
        score += (df['LoginAttempts'] >= 3).astype(float) * 3.0
        score += (df['LoginAttempts'] >= 5).astype(float) * 2.0

    # Very large transaction amount relative to account balance
    if 'TransactionAmount' in df.columns and 'AccountBalance' in df.columns:
        ratio = df['TransactionAmount'] / (df['AccountBalance'].clip(lower=1))
        score += (ratio > 0.8).astype(float) * 2.5
        score += (ratio > 1.5).astype(float) * 2.0

    # Extremely large amounts (top 5%)
    if 'TransactionAmount' in df.columns:
        p95 = df['TransactionAmount'].quantile(0.95)
        score += (df['TransactionAmount'] > p95).astype(float) * 1.5

    # Very short or very long transaction duration
    if 'TransactionDuration' in df.columns:
        p5 = df['TransactionDuration'].quantile(0.05)
        p95 = df['TransactionDuration'].quantile(0.95)
        score += ((df['TransactionDuration'] < p5) | (df['TransactionDuration'] > p95)).astype(float) * 1.0

    # Online channel has more fraud
    if 'Channel' in df.columns:
        score += (df['Channel'].str.lower() == 'online').astype(float) * 0.5

    # Add some random noise for realistic distribution
    np.random.seed(42)
    score += np.random.exponential(0.3, len(df))

    # Label top ~12% as fraud
    threshold = np.percentile(score, 88)
    fraud = (score >= threshold).astype(int)
    print(f"Generated fraud labels: {fraud.sum()} fraud ({fraud.mean()*100:.1f}%) out of {len(fraud)}")
    return fraud


def load_and_preprocess(path: str):
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows, columns: {list(df.columns)}")

    # ---- Check or generate target column ----
    target_col = None
    for c in df.columns:
        if c.lower() in ['isfraud', 'is_fraud', 'fraud', 'fraudulent']:
            target_col = c
            break
    if target_col is None:
        print("No IsFraud column found. Generating labels from domain heuristics...")
        df['IsFraud'] = generate_fraud_labels(df)
        target_col = 'IsFraud'
    print(f"Target column: '{target_col}'")

    # ---- Drop non-informative ID columns ----
    drop_cols = []
    for c in df.columns:
        if c.lower() in ['transactionid', 'transaction_id', 'accountid', 'account_id',
                         'deviceid', 'device_id', 'merchantid', 'merchant_id',
                         'ip address', 'ip_address']:
            drop_cols.append(c)
    df.drop(columns=drop_cols, inplace=True, errors='ignore')
    print(f"Dropped ID columns: {drop_cols}")

    # ---- Parse dates ----
    for c in df.columns:
        if 'date' in c.lower() or 'time' in c.lower():
            try:
                df[c] = pd.to_datetime(df[c], errors='coerce')
            except Exception:
                pass

    # ---- Feature engineering ----
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

    # ---- Drop raw date columns ----
    date_cols = [c for c in df.columns if df[c].dtype == 'datetime64[ns]']
    df.drop(columns=date_cols, inplace=True)

    # ---- Encode categoricals ----
    encoders = {}
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    cat_cols = [c for c in cat_cols if c != target_col]
    for c in cat_cols:
        le = LabelEncoder()
        df[c] = le.fit_transform(df[c].astype(str))
        encoders[c] = le

    # ---- Fill missing values ----
    df.fillna(df.median(numeric_only=True), inplace=True)

    X = df.drop(columns=[target_col])
    y = df[target_col].astype(int)
    print(f"Features: {list(X.columns)}")
    print(f"Class distribution:\n{y.value_counts()}")
    return X, y, encoders, list(X.columns)


def train():
    X, y, encoders, feature_names = load_and_preprocess(DATA_PATH)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ---- SMOTE for class imbalance ----
    print("\nApplying SMOTE for class balance...")
    sm = SMOTE(random_state=42, k_neighbors=min(5, y_train.sum() - 1))
    X_res, y_res = sm.fit_resample(X_train, y_train)
    print(f"After SMOTE - 0: {(y_res==0).sum()}, 1: {(y_res==1).sum()}")

    # ---- Scale ----
    scaler = StandardScaler()
    X_res_sc = scaler.fit_transform(X_res)
    X_test_sc = scaler.transform(X_test)

    results = {}

    # ---- Logistic Regression ----
    print("\nTraining Logistic Regression...")
    lr = LogisticRegression(max_iter=1000, C=1.0, class_weight='balanced', random_state=42)
    lr.fit(X_res_sc, y_res)
    lr_pred = lr.predict(X_test_sc)
    lr_proba = lr.predict_proba(X_test_sc)[:, 1]
    results['logistic_regression'] = {
        'auc_roc': round(roc_auc_score(y_test, lr_proba), 4),
        'f1': round(f1_score(y_test, lr_pred, zero_division=0), 4),
        'precision': round(precision_score(y_test, lr_pred, zero_division=0), 4),
        'recall': round(recall_score(y_test, lr_pred, zero_division=0), 4),
        'avg_precision': round(average_precision_score(y_test, lr_proba), 4),
    }
    print(f"  LR AUC-ROC: {results['logistic_regression']['auc_roc']}")
    print(classification_report(y_test, lr_pred))

    # ---- Random Forest ----
    print("\nTraining Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=200, max_depth=15, min_samples_split=5,
        class_weight='balanced', random_state=42, n_jobs=-1
    )
    rf.fit(X_res, y_res)  # RF doesn't need scaling
    rf_pred = rf.predict(X_test)
    rf_proba = rf.predict_proba(X_test)[:, 1]
    results['random_forest'] = {
        'auc_roc': round(roc_auc_score(y_test, rf_proba), 4),
        'f1': round(f1_score(y_test, rf_pred, zero_division=0), 4),
        'precision': round(precision_score(y_test, rf_pred, zero_division=0), 4),
        'recall': round(recall_score(y_test, rf_pred, zero_division=0), 4),
        'avg_precision': round(average_precision_score(y_test, rf_proba), 4),
    }
    print(f"  RF AUC-ROC: {results['random_forest']['auc_roc']}")
    print(classification_report(y_test, rf_pred))

    # ---- Select best model by AUC-ROC ----
    best_name = max(results, key=lambda k: results[k]['auc_roc'])
    print(f"\nBest model: {best_name} (AUC={results[best_name]['auc_roc']})")

    # ---- Feature importances ----
    if best_name == 'random_forest':
        importances = dict(zip(feature_names, rf.feature_importances_.tolist()))
    else:
        importances = dict(zip(feature_names, abs(lr.coef_[0]).tolist()))
    # Sort
    importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))

    # ---- Save artifacts ----
    joblib.dump(rf, os.path.join(ARTIFACTS_DIR, 'rf_model.pkl'))
    joblib.dump(lr, os.path.join(ARTIFACTS_DIR, 'lr_model.pkl'))
    joblib.dump(scaler, os.path.join(ARTIFACTS_DIR, 'scaler.pkl'))
    joblib.dump(encoders, os.path.join(ARTIFACTS_DIR, 'encoders.pkl'))

    metrics_payload = {
        'best_model': best_name,
        'feature_names': feature_names,
        'models': results,
        'feature_importances': importances,
        'data_info': {
            'total_samples': len(y),
            'fraud_samples': int(y.sum()),
            'legit_samples': int((y == 0).sum()),
            'fraud_rate': round(float(y.mean()) * 100, 2),
        }
    }
    with open(os.path.join(ARTIFACTS_DIR, 'metrics.json'), 'w') as f:
        json.dump(metrics_payload, f, indent=2)

    print(f"\n✅ Artifacts saved to {ARTIFACTS_DIR}")
    print(json.dumps(metrics_payload, indent=2))
    return metrics_payload


if __name__ == '__main__':
    train()
