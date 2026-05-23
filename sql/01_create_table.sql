-- Step 1: Create the energy readings table
CREATE TABLE energy_readings (
    meter_id    VARCHAR(10)  NOT NULL,
    timestamp   TIMESTAMPTZ  NOT NULL,
    power       FLOAT        NOT NULL,
    voltage     FLOAT        NOT NULL,
    current_a   FLOAT        NOT NULL,
    frequency   FLOAT        NOT NULL,
    energy      FLOAT        NOT NULL
);