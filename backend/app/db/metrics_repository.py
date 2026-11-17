from psycopg.rows import dict_row

from backend.app.db.database import get_connection
from backend.app.models.metrics import DeviceMetricCreate


def record_metric(
    device_id: str,
    metrics: DeviceMetricCreate,
) -> dict:
    query = """
        INSERT INTO device_metrics (
            device_id,
            cpu_percent,
            memory_used_percent,
            disk_used_percent
        )
        VALUES (%s, %s, %s, %s)
        RETURNING *
    """

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                query,
                (
                    device_id,
                    metrics.cpu_percent,
                    metrics.memory_used_percent,
                    metrics.disk_used_percent,
                ),
            )
            return cursor.fetchone()


def list_device_metrics(
    device_id: str,
    limit: int = 100,
) -> list[dict]:
    query = """
        SELECT *
        FROM device_metrics
        WHERE device_id = %s
        ORDER BY collected_at DESC
        LIMIT %s
    """

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, (device_id, limit))
            return cursor.fetchall()
