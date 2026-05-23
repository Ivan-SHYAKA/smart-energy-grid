-- Step 6: Continuous aggregates

CREATE MATERIALIZED VIEW energy_readings_15min
WITH (timescaledb.continuous) AS
SELECT meter_id,
       time_bucket('15 minutes', timestamp) AS bucket,
       AVG(power) as avg_power,
       MAX(power) as max_power,
       SUM(energy) as total_energy
FROM energy_readings
GROUP BY meter_id, bucket;

CREATE MATERIALIZED VIEW energy_readings_hourly
WITH (timescaledb.continuous) AS
SELECT meter_id,
       time_bucket('1 hour', timestamp) AS bucket,
       AVG(power) as avg_power,
       MAX(power) as max_power,
       SUM(energy) as total_energy
FROM energy_readings
GROUP BY meter_id, bucket;

CREATE MATERIALIZED VIEW energy_readings_daily
WITH (timescaledb.continuous) AS
SELECT meter_id,
       time_bucket('1 day', timestamp) AS bucket,
       AVG(power) as avg_power,
       MAX(power) as max_power,
       SUM(energy) as total_energy
FROM energy_readings
GROUP BY meter_id, bucket;

SELECT add_continuous_aggregate_policy('energy_readings_15min',
    start_offset => INTERVAL '3 days',
    end_offset   => INTERVAL '1 hour',
    schedule_interval => INTERVAL '15 minutes');

SELECT add_continuous_aggregate_policy('energy_readings_hourly',
    start_offset => INTERVAL '7 days',
    end_offset   => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

SELECT add_continuous_aggregate_policy('energy_readings_daily',
    start_offset => INTERVAL '30 days',
    end_offset   => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');

CALL refresh_continuous_aggregate('energy_readings_15min',
    NOW() - INTERVAL '4 weeks', NOW());
CALL refresh_continuous_aggregate('energy_readings_hourly',
    NOW() - INTERVAL '4 weeks', NOW());
CALL refresh_continuous_aggregate('energy_readings_daily',
    NOW() - INTERVAL '4 weeks', NOW());