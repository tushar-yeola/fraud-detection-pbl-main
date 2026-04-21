from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.db import get_db, Transaction
from typing import Optional
from fastapi import Query

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
def list_alerts(
    db: Session = Depends(get_db),
    resolved: Optional[bool] = False,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    q = db.query(Transaction).filter(Transaction.is_fraud == True)
    if resolved is not None:
        q = q.filter(Transaction.is_resolved == resolved)
    total = q.count()
    items = q.order_by(desc(Transaction.fraud_probability)).offset((page - 1) * limit).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "items": [_serialize_alert(t) for t in items]
    }


@router.patch("/{tx_id}/resolve")
def resolve_alert(tx_id: str, db: Session = Depends(get_db)):
    t = db.query(Transaction).filter(Transaction.transaction_id == tx_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    t.is_resolved = True
    t.is_reviewed = True
    db.commit()
    return {"message": "Alert resolved", "transaction_id": tx_id}


@router.patch("/{tx_id}/review")
def review_alert(tx_id: str, db: Session = Depends(get_db)):
    t = db.query(Transaction).filter(Transaction.transaction_id == tx_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    t.is_reviewed = True
    db.commit()
    return {"message": "Alert marked as reviewed", "transaction_id": tx_id}


def _serialize_alert(t: Transaction):
    return {
        "transaction_id": t.transaction_id,
        "account_id": t.account_id,
        "amount": t.amount,
        "location": t.location,
        "channel": t.channel,
        "fraud_probability": t.fraud_probability,
        "risk_level": t.risk_level,
        "is_reviewed": t.is_reviewed,
        "is_resolved": t.is_resolved,
        "transaction_date": t.transaction_date.isoformat() if t.transaction_date else None,
        "customer_occupation": t.customer_occupation,
        "login_attempts": t.login_attempts,
    }
