import sys
sys.path.append('.')

import warnings
warnings.filterwarnings('ignore')

from backend.models.db import init_db
from backend.seed import seed_data

print("Starting init...")
try:
    init_db()
    print("Database Initialized.")
except Exception as e:
    print(f"Error init DB: {e}")

print("Starting seed...")
try:
    seed_data()
    print("Data seeded successfully.")
except Exception as e:
    print(f"Error seeding data: {e}")
