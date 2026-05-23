import paho.mqtt.client as mqtt
import json, time, random, math
from datetime import datetime, timedelta

# ---- Config ----
METER_COUNT  = 1000
MQTT_BROKER  = "54.157.195.201" 
MQTT_PORT    = 1883

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

def generate_meter_ids(n):
    ids = set()
    while len(ids) < n:
        ids.add(str(random.randint(1000000000, 9999999999)))
    return list(ids)

meter_ids = generate_meter_ids(METER_COUNT)
cumulative_energy = {mid: random.uniform(1000, 50000) for mid in meter_ids}

def time_of_day_factor(hour, minute):
    t = hour + minute / 60.0
    base    = 0.2
    morning = 0.8  * math.exp(-0.5 * ((t - 8.0)  / 1.0) ** 2)
    evening = 1.0  * math.exp(-0.5 * ((t - 19.5) / 1.5) ** 2)
    return base + morning + evening

def generate_reading(meter_id, ts):
    factor      = time_of_day_factor(ts.hour, ts.minute)
    meter_base  = (int(meter_id) % 100) / 100.0
    base_power  = 500 + meter_base * 3000
    power       = base_power * factor * random.uniform(0.85, 1.15)
    voltage     = random.gauss(230, 2.0)
    current     = power / voltage
    frequency   = random.gauss(50.0, 0.05)
    energy_kwh  = (power / 1000) * (5 / 60)
    cumulative_energy[meter_id] += energy_kwh
    return {
        "meter_id":  meter_id,
        "timestamp": ts.isoformat(),
        "power":     round(power, 2),
        "voltage":   round(voltage, 2),
        "current_a":   round(current, 4),
        "frequency": round(frequency, 3),
        "energy":    round(cumulative_energy[meter_id], 4)
    }

def simulate_realtime(duration_minutes=60):
    print(f"Simulating {METER_COUNT} meters for {duration_minutes} min...")
    start = datetime.now()
    for interval in range(duration_minutes // 5):
        ts = start + timedelta(minutes=interval * 5)
        for meter_id in meter_ids:
            reading = generate_reading(meter_id, ts)
            client.publish(f"energy/meters/{meter_id}", json.dumps(reading))
        print(f"  Interval {interval+1} published — {ts.strftime('%H:%M')}")
        time.sleep(2)  # Small pause between bursts
    print("Done.")

simulate_realtime(60)