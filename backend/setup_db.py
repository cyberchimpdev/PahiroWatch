import sqlite3
from app.db.database import get_db_connection, init_db
from app.db.seed_data import seed_database

print("=== PahiroWatch Database Setup ===")
print()

# Step 1: Initialize database schema
print("1. Creating database tables...")
init_db()
print("   Tables created successfully.")

# Step 2: Seed pilot locations
print("2. Seeding pilot corridor locations...")
seed_database()

# Step 3: Verify
print()
print("3. Verifying database...")
conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("   Tables found:", len(tables))
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t[0]}")
    count = cursor.fetchone()[0]
    print(f"   - {t[0]}: {count} rows")

print()
print("4. Location details:")
cursor.execute("SELECT id, name, latitude, longitude, baseline_slope_deg FROM locations")
for row in cursor.fetchall():
    print(f"   - {row[0]}: {row[1]} (lat={row[2]}, lon={row[3]}, slope={row[4]} deg)")

print()
print("5. Historical memory:")
cursor.execute("SELECT id, location_id, memory_key FROM agent_memory")
for row in cursor.fetchall():
    print(f"   - {row[0]}: {row[1]} -> {row[2]}")

conn.close()
print()
print("=== Database setup complete ===")
