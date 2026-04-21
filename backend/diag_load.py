import os
import sys
import json
import joblib
import traceback

# Add backend to path
sys.path.append(os.path.abspath('.'))

LOG_FILE = 'diag.log'

def log(msg):
    with open(LOG_FILE, 'a') as f:
        f.write(str(msg) + '\n')

if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

log("Starting diagnosis...")

try:
    from ml.predict import ARTIFACTS_DIR
    log(f"ARTIFACTS_DIR: {ARTIFACTS_DIR}")
    
    files = os.listdir(ARTIFACTS_DIR)
    log(f"Files: {files}")
    
    log("Attempting to load rf_model.pkl...")
    rf = joblib.load(os.path.join(ARTIFACTS_DIR, 'rf_model.pkl'))
    log("✅ Loaded rf_model")
    
    log("Attempting to load lr_model.pkl...")
    lr = joblib.load(os.path.join(ARTIFACTS_DIR, 'lr_model.pkl'))
    log("✅ Loaded lr_model")
    
    log("Attempting to load scaler.pkl...")
    sc = joblib.load(os.path.join(ARTIFACTS_DIR, 'scaler.pkl'))
    log("✅ Loaded scaler")
    
    log("Attempting to load encoders.pkl...")
    enc = joblib.load(os.path.join(ARTIFACTS_DIR, 'encoders.pkl'))
    log("✅ Loaded encoders")
    
    log("Attempting to load metrics.json...")
    with open(os.path.join(ARTIFACTS_DIR, 'metrics.json')) as f:
        met = json.load(f)
    log("✅ Loaded metrics")
    log(f"Feature names: {met.get('feature_names')}")

except Exception as e:
    log(f"❌ Error: {e}")
    log(traceback.format_exc())

log("Diagnosis finished.")
