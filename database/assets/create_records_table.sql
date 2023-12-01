CREATE TABLE IF NOT EXISTS records (
    record_time TIMESTAMPTZ NOT NULL,
    sensor_id CHAR(64) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    PRIMARY KEY(record_time, sensor_id)
);

CREATE INDEX IF NOT EXISTS idx_records_record_time ON records USING BTREE (record_time);
CREATE INDEX IF NOT EXISTS idx_records_record_time ON records USING HASH (sensor_id);