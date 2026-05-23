-- Step 4: Create 3-hour and 1-week chunk tables
CREATE TABLE energy_readings_3h (LIKE energy_readings INCLUDING ALL);
CREATE TABLE energy_readings_week (LIKE energy_readings INCLUDING ALL);

SELECT create_hypertable('energy_readings_3h', 'timestamp',
    chunk_time_interval => INTERVAL '3 hours');

SELECT create_hypertable('energy_readings_week', 'timestamp',
    chunk_time_interval => INTERVAL '1 week');

-- Load identical data into both
INSERT INTO energy_readings_3h SELECT * FROM energy_readings;
INSERT INTO energy_readings_week SELECT * FROM energy_readings;

-- Check chunk distribution
SELECT chunk_name, range_start, range_end
FROM timescaledb_information.chunks
WHERE hypertable_name = 'energy_readings'
ORDER BY range_start;

-- Count chunks per table
SELECT hypertable_name, COUNT(*) as total_chunks
FROM timescaledb_information.chunks
WHERE hypertable_name IN ('energy_readings','energy_readings_3h','energy_readings_week')
GROUP BY hypertable_name
ORDER BY hypertable_name;