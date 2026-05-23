-- Step 5: Compression

-- Record sizes before compression
SELECT hypertable_name,
       pg_size_pretty(hypertable_size(format('%I', hypertable_name)::regclass))
FROM timescaledb_information.hypertables
WHERE hypertable_name IN ('energy_readings','energy_readings_3h','energy_readings_week');

-- Enable compression on all three tables
ALTER TABLE energy_readings SET (
    timescaledb.compress,
    timescaledb.compress_orderby = 'timestamp DESC'
);
SELECT add_compression_policy('energy_readings', INTERVAL '24 hours');

ALTER TABLE energy_readings_3h SET (
    timescaledb.compress,
    timescaledb.compress_orderby = 'timestamp DESC'
);
SELECT add_compression_policy('energy_readings_3h', INTERVAL '24 hours');

ALTER TABLE energy_readings_week SET (
    timescaledb.compress,
    timescaledb.compress_orderby = 'timestamp DESC'
);
SELECT add_compression_policy('energy_readings_week', INTERVAL '24 hours');

-- Compress all chunks immediately
SELECT compress_chunk(c) FROM show_chunks('energy_readings') c;
SELECT compress_chunk(c) FROM show_chunks('energy_readings_3h') c;
SELECT compress_chunk(c) FROM show_chunks('energy_readings_week') c;

-- Record sizes after compression
SELECT hypertable_name,
       pg_size_pretty(hypertable_size(format('%I', hypertable_name)::regclass))
FROM timescaledb_information.hypertables
WHERE hypertable_name IN ('energy_readings','energy_readings_3h','energy_readings_week');

-- Compression ratios
SELECT 'energy_readings' as hypertable_name,
       pg_size_pretty(SUM(after_compression_total_bytes)::bigint) as compressed_size,
       pg_size_pretty(SUM(before_compression_total_bytes)::bigint) as uncompressed_size,
       ROUND(SUM(before_compression_total_bytes)::numeric /
             SUM(after_compression_total_bytes)::numeric, 2) as compression_ratio
FROM chunk_compression_stats('energy_readings')
UNION ALL
SELECT 'energy_readings_3h',
       pg_size_pretty(SUM(after_compression_total_bytes)::bigint),
       pg_size_pretty(SUM(before_compression_total_bytes)::bigint),
       ROUND(SUM(before_compression_total_bytes)::numeric /
             SUM(after_compression_total_bytes)::numeric, 2)
FROM chunk_compression_stats('energy_readings_3h')
UNION ALL
SELECT 'energy_readings_week',
       pg_size_pretty(SUM(after_compression_total_bytes)::bigint),
       pg_size_pretty(SUM(before_compression_total_bytes)::bigint),
       ROUND(SUM(before_compression_total_bytes)::numeric /
             SUM(after_compression_total_bytes)::numeric, 2)
FROM chunk_compression_stats('energy_readings_week');