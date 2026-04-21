import os
import sys

# Add backend to path
sys.path.append(os.path.abspath('.'))

try:
    from ml.predict import _load_artifacts, ARTIFACTS_DIR
    print(f"Artifacts dir: {ARTIFACTS_DIR}")
    print(f"Files in dir: {os.listdir(ARTIFACTS_DIR)}")
    _load_artifacts()
    print("✅ Artifacts loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load artifacts: {e}")
    import traceback
    traceback.print_exc()
