from fastapi import FastAPI, UploadFile, File, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
import io
import uuid
from datetime import datetime

from models.db import init_db, get_db, Transaction
from api.transactions import router as tx_router
from api.dashboard import router as dashboard_router
from api.analytics import router as analytics_router
from api.alerts import router as alerts_router
from ml.predict import predict_transaction, get_metrics

app = FastAPI(
    title="Fraud Detection API",
    description="Banking transaction fraud detection system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tx_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)
app.include_router(alerts_router)


@app.on_event("startup")
def startup():
    init_db()
    from ml.predict import _load_artifacts
    try:
        _load_artifacts()
        print("ML Models preloaded successfully.")
    except Exception as e:
        print("Could not preload ML models. It may not be trained yet:", e)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "fraud-detection-api"}


@app.get("/api/model/info")
def model_info():
    try:
        return get_metrics()
    except Exception as e:
        return {"error": str(e), "message": "Model not trained yet. Run ml/train.py first."}


@app.post("/api/predict/batch")
async def batch_predict(file: UploadFile = File(...)):
    contents = await file.read()
    
    from models.db import SessionLocal
    db = SessionLocal()
    
    results = []
    fraud_detected = 0
    total = 0
    
    try:
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        total = len(df)
        
        objects = []
        for i, row in df.iterrows():
            raw = row.to_dict()
            try:
                pred = predict_transaction(raw)
            except Exception as e:
                # Default empty prediction on failure
                pred = {"is_fraud": False, "fraud_probability": 0.0, "rf_probability": 0.0, "lr_probability": 0.0, "risk_level": "LOW", "fraud_reasons": []}

            if pred.get('is_fraud'):
                fraud_detected += 1
                
            results.append({
                "row": raw.get('TransactionID', str(i)),
                "is_fraud": pred.get('is_fraud', False),
                "rf_probability": pred.get('rf_probability', 0.0),
                "lr_probability": pred.get('lr_probability', 0.0),
                "fraud_probability": pred.get('fraud_probability', 0.0),
                "risk_level": pred.get('risk_level', 'LOW')
            })

            tx_date = datetime.utcnow()
            if 'TransactionDate' in raw:
                try:
                    tx_date = pd.to_datetime(raw['TransactionDate'])
                except:
                    pass

            db_tx = Transaction(
                transaction_id=str(raw.get('TransactionID', uuid.uuid4())),
                account_id=str(raw.get('AccountID', 'UNKNOWN')),
                amount=float(raw.get('TransactionAmount', 0)),
                transaction_type=str(raw.get('TransactionType', 'Unknown')),
                location=str(raw.get('Location', 'Unknown')),
                channel=str(raw.get('Channel', 'Unknown')),
                merchant_id=str(raw.get('MerchantID', 'Unknown')),
                customer_age=int(raw.get('CustomerAge', 0)),
                customer_occupation=str(raw.get('CustomerOccupation', 'Unknown')),
                account_balance=float(raw.get('AccountBalance', 0)),
                transaction_duration=int(raw.get('TransactionDuration', 0)),
                login_attempts=int(raw.get('LoginAttempts', 1)),
                transaction_date=tx_date,
                is_fraud=pred.get('is_fraud', False),
                fraud_probability=pred.get('fraud_probability', 0.0),
                risk_level=pred.get('risk_level', 'LOW'),
                fraud_reasons="|".join(pred.get('fraud_reasons', []))
            )
            objects.append(db_tx)

        db.bulk_save_objects(objects)
        db.commit()
    except Exception as e:
        print("Batch processing error:", e)
        return {"total": 0, "fraud_detected": 0, "fraud_rate": 0, "results": [], "error": str(e)}
    finally:
        db.close()

    fraud_rate = round((fraud_detected / total * 100), 2) if total > 0 else 0
    return {
        "total": total,
        "fraud_detected": fraud_detected,
        "fraud_rate": fraud_rate,
        "results": results
    }
