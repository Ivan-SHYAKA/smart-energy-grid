import psycopg2
from psycopg2.extras import execute_values
import random, math
from datetime import datetime, timedelta

DB_CONFIG = {
    "host":     "localhost",      
    "port":     5432,
    "dbname":   "energy_db",
    "user":     "energy_user",
    "password": "StrongPassword123!"
}

METER_COUNT = 1000
WEEKS       = 4
BATCH_SIZE  = 50000 

# Re-use same functions from simulator.py
def generate_meter_ids(n):
    ids = set()
    while len(ids) < n:
        ids.add(str(random.randint(1000000000, 9999999999)))
    return list(ids)

def time_of_day_factor(hour, minute):
    t = hour + minute / 60.0
    return 0.2 + 0.8*math.exp(-0.5*((t-8.0)/1.0)**2) + 1.0*math.exp(-0.5*((t-19.5)/1.5)**2)

meter_ids         = generate_meter_ids(METER_COUNT)
cumulative_energy = {mid: random.uniform(1000, 50000) for mid in meter_ids}

conn = psycopg2.connect(**DB_CONFIG)
cur  = conn.cursor()

start_date = datetime.now() - timedelta(weeks=WEEKS)
end_date   = datetime.now()
current    = start_date
batch      = []
total_rows = 0

print(f"Loading {WEEKS} weeks of data from {start_date.date()} to {end_date.date()}...")
print(f"Expected rows: ~{METER_COUNT * 288 * WEEKS * 7:,}")

while current < end_date:
    factor = time_of_day_factor(current.hour, current.minute)
    for meter_id in meter_ids:
        meter_base = (int(meter_id) % 100) / 100.0
        power      = (500 + meter_base * 3000) * factor * random.uniform(0.85, 1.15)
        voltage    = random.gauss(230, 2.0)
        current_a  = power / voltage
        freq       = random.gauss(50.0, 0.05)
        energy_kwh = (power / 1000) * (5 / 60)
        cumulative_energy[meter_id] += energy_kwh
        batch.append((
            meter_id, current.isoformat(),
            round(power, 2), round(voltage, 2),
            round(current_a, 4), round(freq, 3),
            round(cumulative_energy[meter_id], 4)
        ))

    if len(batch) >= BATCH_SIZE:
        execute_values(cur, """
            INSERT INTO energy_readings
                (meter_id, timestamp, power, voltage, current_a, frequency, energy)
            VALUES %s
        """, batch)
        conn.commit()
        total_rows += len(batch)
        print(f"  Inserted {total_rows:,} rows | Current timestamp: {current.strftime('%Y-%m-%d %H:%M')}")
        batch = []

    current += timedelta(minutes=5)

if batch:
    execute_values(cur, """
        INSERT INTO energy_readings
            (meter_id, timestamp, power, voltage, current_a, frequency, energy)
        VALUES %s
    """, batch)
    conn.commit()
    total_rows += len(batch)

print(f"\nDone! Total rows inserted: {total_rows:,}")
cur.execute("SELECT COUNT(*) FROM energy_readings")
print(f"Verified row count: {cur.fetchone()[0]:,}")
conn.close()