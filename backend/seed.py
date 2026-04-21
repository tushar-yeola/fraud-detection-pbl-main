import sqlite3
import uuid
import random
from datetime import datetime, timedelta

DB_PATH = "fraud_detection.db"
NUM_TX = 40

channels = ["Online", "ATM", "Branch", "Mobile"]
locations = ["New York", "London", "San Francisco", "Tokyo", "Berlin", "Dubai"]
occupations = ["Engineer", "Doctor", "Student", "Retired", "Teacher", "Other"]
types = ["Debit", "Credit", "Transfer"]

def seed_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions';")
    if not c.fetchone():
        print("transactions table does not exist. Please run backend first.")
        return

    now = datetime.utcnow()
    
    for i in range(NUM_TX):
        is_fraud = random.random() < 0.15 # 15% fraud
        
        tx_id = str(uuid.uuid4())
        acc_id = f"ACC{random.randint(100, 999)}"
        amount = round(random.uniform(5.0, 5000.0), 2)
        
        if is_fraud:
            amount = round(random.uniform(2000.0, 15000.0), 2)
            
        tx_type = random.choice(types)
        loc = random.choice(locations)
        channel = random.choice(channels)
        merchant = f"Merchant_{random.randint(1, 50)}"
        age = random.randint(18, 80)
        occ = random.choice(occupations)
        bal = round(random.uniform(100.0, 50000.0), 2)
        dur = random.randint(10, 600)
        login = random.randint(1, 5)
        
        if is_fraud:
            login = random.randint(3, 10)
            
        # Distribute over last 7 days
        days_ago = random.uniform(0, 7)
        tx_date = now - timedelta(days=days_ago)
        
        prob = random.uniform(0.6, 0.99) if is_fraud else random.uniform(0.01, 0.3)
        risk = "HIGH" if prob >= 0.75 else "MEDIUM" if prob >= 0.4 else "LOW"
        
        c.execute('''
            INSERT INTO transactions (
                transaction_id, account_id, amount, transaction_type, location, channel, 
                merchant_id, customer_age, customer_occupation, account_balance, 
                transaction_duration, login_attempts, transaction_date, 
                is_fraud, fraud_probability, risk_level, is_reviewed, is_resolved, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tx_id, acc_id, amount, tx_type, loc, channel, merchant, age, occ, bal,
            dur, login, tx_date.isoformat(),
            is_fraud, prob, risk, False, False, tx_date.isoformat()
        ))
        
    conn.commit()
    conn.close()
    print(f"Successfully seeded {NUM_TX} transactions!")

if __name__ == "__main__":
    seed_data()
