from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.db import get_db, Transaction
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Transaction.id)).scalar() or 0
    fraud_count = db.query(func.count(Transaction.id)).filter(Transaction.is_fraud == True).scalar() or 0
    total_amount = db.query(func.sum(Transaction.amount)).scalar() or 0.0
    fraud_amount = db.query(func.sum(Transaction.amount)).filter(Transaction.is_fraud == True).scalar() or 0.0
    high_risk = db.query(func.count(Transaction.id)).filter(Transaction.risk_level == 'HIGH').scalar() or 0
    unresolved = db.query(func.count(Transaction.id)).filter(
        Transaction.is_fraud == True, Transaction.is_resolved == False
    ).scalar() or 0

    fraud_rate = round((fraud_count / total * 100), 2) if total > 0 else 0.0

    # Last 7 days trend
    now = datetime.utcnow()
    trend = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59)
        day_total = db.query(func.count(Transaction.id)).filter(
            Transaction.created_at.between(day_start, day_end)
        ).scalar() or 0
        day_fraud = db.query(func.count(Transaction.id)).filter(
            Transaction.created_at.between(day_start, day_end),
            Transaction.is_fraud == True
        ).scalar() or 0
        trend.append({
            "date": day.strftime("%b %d"),
            "total": day_total,
            "fraud": day_fraud
        })

    return {
        "total_transactions": total,
        "fraud_count": fraud_count,
        "fraud_rate": fraud_rate,
        "total_amount": round(total_amount, 2),
        "fraud_amount": round(fraud_amount, 2),
        "high_risk_count": high_risk,
        "unresolved_alerts": unresolved,
        "trend": trend,
    }
