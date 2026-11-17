from psycopg.rows import dict_row

from backend.app.db.database import get_connection
from backend.app.models.device import DeviceInventory


OFFLINE_THRESHOLD_SECONDS = 120


def mark_offline_devices() -> int:
    query = """
        UPDATE devices
        SET status = 'offline'
        WHERE status <> 'offline'
          AND last_seen < (
              CURRENT_TIMESTAMP
              - (%s * INTERVAL '1 second')
          )
        RETURNING device_id
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (OFFLINE_THRESHOLD_SECONDS,),
            )
            return len(cursor.fetchall())


def upsert_device(inventory: DeviceInventory) -> dict:
    data = inventory.model_dump()

    query = """
        INSERT INTO devices (
            device_id, hostname, os_name, os_version, architecture,
            cpu_cores, cpu_percent, memory_total_bytes,
            memory_used_percent, disk_total_bytes, disk_used_percent,
            registered_at, last_seen, status
        )
        VALUES (
            %(device_id)s, %(hostname)s, %(os_name)s, %(os_version)s,
            %(architecture)s, %(cpu_cores)s, %(cpu_percent)s,
            %(memory_total_bytes)s, %(memory_used_percent)s,
            %(disk_total_bytes)s, %(disk_used_percent)s,
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'online'
        )
        ON CONFLICT (device_id) DO UPDATE SET
            hostname = EXCLUDED.hostname,
            os_name = EXCLUDED.os_name,
            os_version = EXCLUDED.os_version,
            architecture = EXCLUDED.architecture,
            cpu_cores = EXCLUDED.cpu_cores,
            cpu_percent = EXCLUDED.cpu_percent,
            memory_total_bytes = EXCLUDED.memory_total_bytes,
            memory_used_percent = EXCLUDED.memory_used_percent,
            disk_total_bytes = EXCLUDED.disk_total_bytes,
            disk_used_percent = EXCLUDED.disk_used_percent,
            last_seen = CURRENT_TIMESTAMP,
            status = 'online'
        RETURNING *
    """

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, data)
            return cursor.fetchone()


def list_devices() -> list[dict]:
    mark_offline_devices()

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT * FROM devices ORDER BY hostname")
            return cursor.fetchall()


def get_device(device_id: str) -> dict | None:
    mark_offline_devices()

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT * FROM devices WHERE device_id = %s",
                (device_id,),
            )
            return cursor.fetchone()


def update_device_heartbeat(device_id: str) -> dict | None:
    query = """
        UPDATE devices
        SET last_seen = CURRENT_TIMESTAMP,
            status = 'online'
        WHERE device_id = %s
        RETURNING *
    """

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, (device_id,))
            return cursor.fetchone()
