from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'fraud_detection.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    account_id = Column(String, index=True)
    amount = Column(Float)
    transaction_type = Column(String)
    location = Column(String)
    channel = Column(String)
    merchant_id = Column(String)
    customer_age = Column(Integer)
    customer_occupation = Column(String)
    account_balance = Column(Float)
    transaction_duration = Column(Integer)
    login_attempts = Column(Integer)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    previous_transaction_date = Column(DateTime, nullable=True)

    # ML Output
    is_fraud = Column(Boolean, default=False)
    fraud_probability = Column(Float, default=0.0)
    risk_level = Column(String, default='LOW')
    fraud_reasons = Column(String, default='')

    # Status
    is_reviewed = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
