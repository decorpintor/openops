
import pytest
from fastapi.testclient import TestClient

from backend.app.db.database import get_connection
from backend.app.main import app


@pytest.fixture(autouse=True)
def clean_test_devices():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM devices WHERE device_id LIKE 'test-device-%'"
            )

    yield

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM devices WHERE device_id LIKE 'test-device-%'"
            )


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def device_payload():
    return {
        "device_id": "test-device-001",
        "hostname": "OPENOPS-TEST",
        "os_name": "Linux",
        "os_version": "Ubuntu 24.04",
        "architecture": "x86_64",
        "cpu_cores": 4,
        "cpu_percent": 12.5,
        "memory_total_bytes": 8589934592,
        "memory_used_percent": 35.0,
        "disk_total_bytes": 100000000000,
        "disk_used_percent": 40.0,
    }


def test_register_device(client, device_payload):
    response = client.post(
        "/api/v1/devices/register",
        json=device_payload,
    )

    assert response.status_code == 201
    data = response.json()

    assert data["device_id"] == device_payload["device_id"]
    assert data["hostname"] == device_payload["hostname"]
    assert data["status"] == "online"
    assert "registered_at" in data
    assert "last_seen" in data


def test_list_devices(client, device_payload):
    client.post("/api/v1/devices/register", json=device_payload)

    response = client.get("/api/v1/devices")

    assert response.status_code == 200

    devices = response.json()
    test_devices = [
        device for device in devices
        if device["device_id"] == "test-device-001"
    ]

    assert len(test_devices) == 1
    assert test_devices[0]["hostname"] == "OPENOPS-TEST"


def test_get_device(client, device_payload):
    client.post("/api/v1/devices/register", json=device_payload)

    response = client.get("/api/v1/devices/test-device-001")

    assert response.status_code == 200
    assert response.json()["hostname"] == "OPENOPS-TEST"


def test_device_heartbeat(client, device_payload):
    client.post("/api/v1/devices/register", json=device_payload)

    response = client.post(
        "/api/v1/devices/test-device-001/heartbeat"
    )

    assert response.status_code == 200
    assert response.json()["device_id"] == "test-device-001"
    assert response.json()["status"] == "online"


def test_unknown_device_returns_404(client):
    response = client.get("/api/v1/devices/unknown-device")

    assert response.status_code == 404


def test_reregistration_preserves_registered_at(client, device_payload):
    first = client.post(
        "/api/v1/devices/register",
        json=device_payload,
    )
    original_registered_at = first.json()["registered_at"]

    updated_payload = {
        **device_payload,
        "cpu_percent": 75.0,
    }

    second = client.post(
        "/api/v1/devices/register",
        json=updated_payload,
    )

    assert second.status_code == 201
    assert second.json()["registered_at"] == original_registered_at
    assert second.json()["cpu_percent"] == 75.0




def test_device_marked_offline_after_stale_heartbeat(
    client,
    device_payload,
):
    client.post(
        "/api/v1/devices/register",
        json=device_payload,
    )

    # Simulate a device that has not reported for three minutes.
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE devices
                SET last_seen = CURRENT_TIMESTAMP - INTERVAL '3 minutes'
                WHERE device_id = %s
                """,
                ("test-device-001",),
            )

    response = client.get("/api/v1/devices/test-device-001")

    assert response.status_code == 200
    assert response.json()["status"] == "offline"


def test_heartbeat_restores_offline_device_online(
    client,
    device_payload,
):
    client.post(
        "/api/v1/devices/register",
        json=device_payload,
    )

    # Simulate an expired heartbeat.
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE devices
                SET last_seen = CURRENT_TIMESTAMP - INTERVAL '3 minutes'
                WHERE device_id = %s
                """,
                ("test-device-001",),
            )

    # First request refreshes the stale status.
    offline_response = client.get(
        "/api/v1/devices/test-device-001"
    )
    assert offline_response.json()["status"] == "offline"

    # A new heartbeat should restore online status.
    heartbeat_response = client.post(
        "/api/v1/devices/test-device-001/heartbeat"
    )

    assert heartbeat_response.status_code == 200
    assert heartbeat_response.json()["status"] == "online"
