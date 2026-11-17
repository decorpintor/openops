

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, status

from backend.app.db.device_repository import (
    get_device as db_get_device,
    list_devices as db_list_devices,
    mark_offline_devices,
    update_device_heartbeat,
    upsert_device,
)

from backend.app.db.metrics_repository import (
    list_device_metrics,
    record_metric,
)

from backend.app.models.device import (
    DeviceInventory,
    DeviceRecord,
    HeartbeatResponse,
)

from backend.app.models.metrics import (
    DeviceMetricCreate,
    DeviceMetricRecord,
)


OFFLINE_CHECK_INTERVAL_SECONDS = 30


async def offline_device_monitor():
    """Periodically mark devices offline when heartbeats become stale."""

    while True:
        try:
            updated_count = await asyncio.to_thread(
                mark_offline_devices
            )

            if updated_count:
                print(
                    f"OpenOps: marked {updated_count} "
                    "device(s) offline"
                )

        except Exception as exc:
            print(f"OpenOps offline monitor error: {exc}")

        await asyncio.sleep(OFFLINE_CHECK_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start and stop the background offline-device monitor."""

    monitor_task = asyncio.create_task(
        offline_device_monitor()
    )

    print("OpenOps offline monitor started")

    try:
        yield
    finally:
        monitor_task.cancel()

        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

        print("OpenOps offline monitor stopped")


app = FastAPI(
    title="OpenOps API",
    description="Independent endpoint monitoring and management platform",
    version="0.3.0",
    lifespan=lifespan,
)



@app.get("/")
def root():
    return {
        "application": "OpenOps",
        "status": "running",
        "version": "0.3.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "openops-api",
    }


@app.post(
    "/api/v1/devices/register",
    response_model=DeviceRecord,
    status_code=status.HTTP_201_CREATED,
)
def register_device(inventory: DeviceInventory):
    return upsert_device(inventory)


@app.get(
    "/api/v1/devices",
    response_model=list[DeviceRecord],
)
def list_devices():
    return db_list_devices()


@app.get(
    "/api/v1/devices/{device_id}",
    response_model=DeviceRecord,
)
def get_device(device_id: str):
    device = db_get_device(device_id)

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    return device


@app.post(
    "/api/v1/devices/{device_id}/heartbeat",
    response_model=HeartbeatResponse,
)
def receive_heartbeat(device_id: str):
    device = update_device_heartbeat(device_id)

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    return HeartbeatResponse(
        device_id=device["device_id"],
        status=device["status"],
        last_seen=device["last_seen"],
    )



@app.post(
    "/api/v1/devices/{device_id}/metrics",
    response_model=DeviceMetricRecord,
    status_code=status.HTTP_201_CREATED,
)
def submit_device_metrics(
    device_id: str,
    metrics: DeviceMetricCreate,
):
    device = db_get_device(device_id)

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    return record_metric(device_id, metrics)


@app.get(
    "/api/v1/devices/{device_id}/metrics",
    response_model=list[DeviceMetricRecord],
)
def get_device_metrics(
    device_id: str,
    limit: int = Query(default=100, ge=1, le=1000),
):
    device = db_get_device(device_id)

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    return list_device_metrics(device_id, limit)
