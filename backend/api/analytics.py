from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from models.db import get_db, Transaction

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/fraud-by-channel")
def fraud_by_channel(db: Session = Depends(get_db)):
    rows = db.query(
        Transaction.channel,
        func.count(Transaction.id).label("total"),
        func.sum(func.cast(Transaction.is_fraud, Integer)).label("fraud")
    ).group_by(Transaction.channel).all()
    return [{"channel": r.channel or "Unknown", "total": r.total, "fraud": r.fraud or 0} for r in rows]


@router.get("/fraud-by-occupation")
def fraud_by_occupation(db: Session = Depends(get_db)):
    rows = db.query(
        Transaction.customer_occupation,
        func.count(Transaction.id).label("total"),
        func.sum(func.cast(Transaction.is_fraud, Integer)).label("fraud")
    ).group_by(Transaction.customer_occupation).all()
    return [{"occupation": r.customer_occupation or "Unknown", "total": r.total, "fraud": r.fraud or 0} for r in rows]


@router.get("/fraud-by-location")
def fraud_by_location(db: Session = Depends(get_db)):
    rows = db.query(
        Transaction.location,
        func.count(Transaction.id).label("total"),
        func.sum(func.cast(Transaction.is_fraud, Integer)).label("fraud")
    ).group_by(Transaction.location).order_by(func.count(Transaction.id).desc()).limit(15).all()
    return [{"location": r.location or "Unknown", "total": r.total, "fraud": r.fraud or 0} for r in rows]


@router.get("/amount-distribution")
def amount_distribution(db: Session = Depends(get_db)):
    buckets = [
        (0, 100, "0-100"),
        (100, 500, "100-500"),
        (500, 1000, "500-1K"),
        (1000, 5000, "1K-5K"),
        (5000, 10000, "5K-10K"),
        (10000, 999999, "10K+"),
    ]
    result = []
    for lo, hi, label in buckets:
        total = db.query(func.count(Transaction.id)).filter(
            Transaction.amount >= lo, Transaction.amount < hi
        ).scalar() or 0
        fraud = db.query(func.count(Transaction.id)).filter(
            Transaction.amount >= lo, Transaction.amount < hi,
            Transaction.is_fraud == True
        ).scalar() or 0
        result.append({"range": label, "total": total, "fraud": fraud})
    return result


@router.get("/risk-distribution")
def risk_distribution(db: Session = Depends(get_db)):
    rows = db.query(
        Transaction.risk_level,
        func.count(Transaction.id).label("count")
    ).group_by(Transaction.risk_level).all()
    return [{"risk_level": r.risk_level, "count": r.count} for r in rows]


@router.get("/hourly-trend")
def hourly_trend(db: Session = Depends(get_db)):
    result = []
    for hour in range(24):
        total = db.query(func.count(Transaction.id)).filter(
            func.strftime('%H', Transaction.transaction_date) == f"{hour:02d}"
        ).scalar() or 0
        fraud = db.query(func.count(Transaction.id)).filter(
            func.strftime('%H', Transaction.transaction_date) == f"{hour:02d}",
            Transaction.is_fraud == True
        ).scalar() or 0
        result.append({"hour": f"{hour:02d}:00", "total": total, "fraud": fraud})
    return result


@router.get("/transaction-type-split")
def transaction_type_split(db: Session = Depends(get_db)):
    rows = db.query(
        Transaction.transaction_type,
        func.count(Transaction.id).label("total"),
        func.sum(func.cast(Transaction.is_fraud, Integer)).label("fraud")
    ).group_by(Transaction.transaction_type).all()
    return [{"type": r.transaction_type or "Unknown", "total": r.total, "fraud": r.fraud or 0} for r in rows]
