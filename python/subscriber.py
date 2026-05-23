import paho.mqtt.client as mqtt
import psycopg2
import json

# ---- EC2 database connection ----
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "energy_db",
    "user":     "energy_user",
    "password": "StrongPassword123!"
}

conn = psycopg2.connect(**DB_CONFIG)
conn.autocommit = True
cur = conn.cursor()

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to EMQX with code {reason_code}")
    client.subscribe("energy/meters/#")
    print("Subscribed to energy/meters/#")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"Received: {data['meter_id']}")  # Add this line
        cur.execute("""
            INSERT INTO energy_readings
                (meter_id, timestamp, power, voltage, current_a, frequency, energy)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['meter_id'], data['timestamp'],
            data['power'],    data['voltage'],
            data['current_a'], data['frequency'],
            data['energy']
        ))
        print("Inserted OK")
    except Exception as e:
        print(f"Error: {e}")  

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect("54.157.195.201", 1883, 60)
print("Starting subscriber...")
client.loop_forever()