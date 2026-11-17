CREATE TABLE IF NOT EXISTS devices (
    device_id VARCHAR(255) PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    os_name VARCHAR(100) NOT NULL,
    os_version TEXT NOT NULL,
    architecture VARCHAR(100) NOT NULL,
    cpu_cores INTEGER NOT NULL CHECK (cpu_cores >= 1),
    cpu_percent DOUBLE PRECISION NOT NULL CHECK (cpu_percent BETWEEN 0 AND 100),
    memory_total_bytes BIGINT NOT NULL CHECK (memory_total_bytes > 0),
    memory_used_percent DOUBLE PRECISION NOT NULL CHECK (memory_used_percent BETWEEN 0 AND 100),
    disk_total_bytes BIGINT NOT NULL CHECK (disk_total_bytes > 0),
    disk_used_percent DOUBLE PRECISION NOT NULL CHECK (disk_used_percent BETWEEN 0 AND 100),
    registered_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'online'
);

CREATE INDEX IF NOT EXISTS idx_devices_hostname
ON devices(hostname);

CREATE INDEX IF NOT EXISTS idx_devices_status
ON devices(status);

CREATE INDEX IF NOT EXISTS idx_devices_last_seen
ON devices(last_seen);

-- Historical endpoint monitoring metrics
CREATE TABLE IF NOT EXISTS device_metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(255) NOT NULL
        REFERENCES devices(device_id) ON DELETE CASCADE,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cpu_percent DOUBLE PRECISION NOT NULL
        CHECK (cpu_percent BETWEEN 0 AND 100),
    memory_used_percent DOUBLE PRECISION NOT NULL
        CHECK (memory_used_percent BETWEEN 0 AND 100),
    disk_used_percent DOUBLE PRECISION NOT NULL
        CHECK (disk_used_percent BETWEEN 0 AND 100)
);

CREATE INDEX IF NOT EXISTS idx_device_metrics_device_id
ON device_metrics(device_id);

CREATE INDEX IF NOT EXISTS idx_device_metrics_collected_at
ON device_metrics(collected_at);

CREATE INDEX IF NOT EXISTS idx_device_metrics_device_time
ON device_metrics(device_id, collected_at DESC);
