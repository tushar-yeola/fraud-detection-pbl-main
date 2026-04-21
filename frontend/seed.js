import sqlite3 from 'sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';
import { v4 as uuidv4 } from 'uuid';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const dbPath = path.resolve(__dirname, '../backend/fraud_detection.db');
const db = new (sqlite3.verbose()).Database(dbPath);

const NUM_TX = 40;
const channels = ["Online", "ATM", "Branch", "Mobile"];
const locations = ["New York", "London", "San Francisco", "Tokyo", "Berlin", "Dubai"];
const occupations = ["Engineer", "Doctor", "Student", "Retired", "Teacher", "Other"];
const types = ["Debit", "Credit", "Transfer"];

console.log("Connecting to:", dbPath);

db.serialize(() => {
  db.get("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'", (err, row) => {
    if (!row) {
      console.log("transactions table does not exist. Please run backend first to create tables.");
      return;
    }
    
    db.run("BEGIN TRANSACTION");
    const stmt = db.prepare(`
      INSERT INTO transactions (
        transaction_id, account_id, amount, transaction_type, location, channel, 
        merchant_id, customer_age, customer_occupation, account_balance, 
        transaction_duration, login_attempts, transaction_date, 
        is_fraud, fraud_probability, risk_level, is_reviewed, is_resolved, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    let inserted = 0;
    for (let i = 0; i < NUM_TX; i++) {
        const isFraud = Math.random() < 0.15; // roughly 15% fraud
        const txId = uuidv4();
        const accId = `ACC${Math.floor(Math.random() * 900) + 100}`;
        let amount = (Math.random() * 4995) + 5;
        if (isFraud) amount = (Math.random() * 13000) + 2000;
        
        const loc = locations[Math.floor(Math.random() * locations.length)];
        const channel = channels[Math.floor(Math.random() * channels.length)];
        const type = types[Math.floor(Math.random() * types.length)];
        const merchant = `Merchant_${Math.floor(Math.random() * 50) + 1}`;
        const occ = occupations[Math.floor(Math.random() * occupations.length)];
        
        // Random date within last 7 days
        const date = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000);
        
        // Ensure values align
        const prob = isFraud ? (0.6 + Math.random() * 0.39) : (0.01 + Math.random() * 0.29);
        const risk = prob >= 0.75 ? 'HIGH' : prob >= 0.4 ? 'MEDIUM' : 'LOW';

        stmt.run([
            txId, accId, parseFloat(amount.toFixed(2)), type, loc, channel,
            merchant, 18 + Math.floor(Math.random()*60), occ, 1000 + Math.random()*20000,
            10 + Math.floor(Math.random()*200), isFraud ? 5 : 1, date.toISOString().replace('Z',''),
            isFraud ? 1 : 0, prob, risk, 0, 0, date.toISOString().replace('Z','')
        ]);
        inserted++;
    }
    stmt.finalize();
    db.run("COMMIT", err => {
        if(err) console.error("Error committing:", err);
        else console.log(`Successfully seeded ${inserted} dummy transactions using Node.js!`);
    });
  });
});

db.close();
