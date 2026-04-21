from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models.db import get_db, Transaction
from datetime import datetime, timedelta
from typing import Optional
import uuid
from ml.predict import predict_transaction
from pydantic import BaseModel

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


class TransactionIn(BaseModel):
    AccountID: str = "ACC001"
    TransactionAmount: float
    TransactionDate: Optional[str] = None
    TransactionType: str = "Debit"
    Location: str = "New York"
    DeviceID: Optional[str] = None
    MerchantID: Optional[str] = None
    AccountBalance: float = 5000.0
    PreviousTransactionDate: Optional[str] = None
    Channel: str = "Online"
    CustomerAge: int = 35
    CustomerOccupation: str = "Engineer"
    TransactionDuration: int = 120
    LoginAttempts: int = 1


@router.get("")
def list_transactions(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    is_fraud: Optional[bool] = None,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
):
    q = db.query(Transaction)
    if is_fraud is not None:
        q = q.filter(Transaction.is_fraud == is_fraud)
    if risk_level:
        q = q.filter(Transaction.risk_level == risk_level.upper())
    if search:
        q = q.filter(
            Transaction.transaction_id.contains(search) |
            Transaction.account_id.contains(search) |
            Transaction.location.contains(search)
        )
    total = q.count()
    items = q.order_by(desc(Transaction.created_at)).offset((page - 1) * limit).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "items": [_serialize(t) for t in items]
    }


@router.get("/{tx_id}")
def get_transaction(tx_id: str, db: Session = Depends(get_db)):
    t = db.query(Transaction).filter(Transaction.transaction_id == tx_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return _serialize(t)


@router.post("/predict")
def predict_single(tx: TransactionIn, db: Session = Depends(get_db)):
    raw = tx.model_dump()
    # Rename keys to match training
    rename = {
        'AccountID': 'AccountID',
        'TransactionAmount': 'TransactionAmount',
        'TransactionDate': 'TransactionDate',
        'TransactionType': 'TransactionType',
        'Location': 'Location',
        'AccountBalance': 'AccountBalance',
        'PreviousTransactionDate': 'PreviousTransactionDate',
        'Channel': 'Channel',
        'CustomerAge': 'CustomerAge',
        'CustomerOccupation': 'CustomerOccupation',
        'TransactionDuration': 'TransactionDuration',
        'LoginAttempts': 'LoginAttempts',
    }
    result = predict_transaction(raw)

    # Persist to DB
    tx_date = None
    if tx.TransactionDate:
        try:
            tx_date = datetime.fromisoformat(tx.TransactionDate)
        except Exception:
            tx_date = datetime.utcnow()
    else:
        tx_date = datetime.utcnow()

    prev_date = None
    if tx.PreviousTransactionDate:
        try:
            prev_date = datetime.fromisoformat(tx.PreviousTransactionDate)
        except Exception:
            pass

    db_tx = Transaction(
        transaction_id=str(uuid.uuid4()),
        account_id=tx.AccountID,
        amount=tx.TransactionAmount,
        transaction_type=tx.TransactionType,
        location=tx.Location,
        channel=tx.Channel,
        merchant_id=tx.MerchantID or "UNKNOWN",
        customer_age=tx.CustomerAge,
        customer_occupation=tx.CustomerOccupation,
        account_balance=tx.AccountBalance,
        transaction_duration=tx.TransactionDuration,
        login_attempts=tx.LoginAttempts,
        transaction_date=tx_date,
        previous_transaction_date=prev_date,
        is_fraud=result['is_fraud'],
        fraud_probability=result['fraud_probability'],
        risk_level=result['risk_level'],
        fraud_reasons="|".join(result.get('fraud_reasons', [])),
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return {**result, "transaction_id": db_tx.transaction_id}


def _serialize(t: Transaction):
    return {
        "id": t.id,
        "transaction_id": t.transaction_id,
        "account_id": t.account_id,
        "amount": t.amount,
        "transaction_type": t.transaction_type,
        "location": t.location,
        "channel": t.channel,
        "merchant_id": t.merchant_id,
        "customer_age": t.customer_age,
        "customer_occupation": t.customer_occupation,
        "account_balance": t.account_balance,
        "transaction_duration": t.transaction_duration,
        "login_attempts": t.login_attempts,
        "transaction_date": t.transaction_date.isoformat() if t.transaction_date else None,
        "is_fraud": t.is_fraud,
        "fraud_probability": t.fraud_probability,
        "risk_level": t.risk_level,
        "fraud_reasons": t.fraud_reasons.split('|') if getattr(t, 'fraud_reasons', '') else [],
        "is_reviewed": t.is_reviewed,
        "is_resolved": t.is_resolved,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }
