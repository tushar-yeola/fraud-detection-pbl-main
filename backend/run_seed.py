import sys
sys.path.append('.')
from backend.models.db import init_db
from backend.seed import seed_data

print("Initializing DB...")
init_db()
print("Seeding data...")
seed_data()
