import os
import time

import httpx

from agent.collectors.system_info import collect_system_info


API_URL = os.getenv(
    "OPENOPS_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

INTERVAL_SECONDS = int(
    os.getenv("OPENOPS_INTERVAL_SECONDS", "60")
)

if INTERVAL_SECONDS < 1:
    raise ValueError("OPENOPS_INTERVAL_SECONDS must be at least 1")


def run_cycle(client: httpx.Client):
    inventory = collect_system_info()
    device_id = inventory["device_id"]

    metrics = {
        "cpu_percent": inventory["cpu_percent"],
        "memory_used_percent": inventory["memory_used_percent"],
        "disk_used_percent": inventory["disk_used_percent"],
    }

    print("\n===== OPENOPS MONITORING CYCLE =====")
    print(f"Hostname: {inventory['hostname']}")
    print(f"Device ID: {device_id}")

    # Register or update endpoint inventory.
    registration = client.post(
        f"{API_URL}/api/v1/devices/register",
        json=inventory,
    )
    registration.raise_for_status()
    print("PASS: Device registered")

    # Send endpoint heartbeat.
    heartbeat = client.post(
        f"{API_URL}/api/v1/devices/{device_id}/heartbeat"
    )
    heartbeat.raise_for_status()
    print("PASS: Heartbeat received")

    # Submit historical system metrics.
    metric_response = client.post(
        f"{API_URL}/api/v1/devices/{device_id}/metrics",
        json=metrics,
    )
    metric_response.raise_for_status()

    print("PASS: Historical metrics submitted")
    print(f"Metrics: {metric_response.json()}")


def main():
    print("===== OPENOPS ENDPOINT AGENT =====")
    print(f"API: {API_URL}")
    print(f"Monitoring interval: {INTERVAL_SECONDS} seconds")
    print("Press Ctrl+C to stop the agent.")

    try:
        with httpx.Client(timeout=15.0) as client:
            while True:
                try:
                    run_cycle(client)

                except httpx.HTTPError as exc:
                    print(f"ERROR: API communication failed: {exc}")

                except Exception as exc:
                    print(f"ERROR: Monitoring cycle failed: {exc}")

                print(
                    f"\nNext monitoring cycle in "
                    f"{INTERVAL_SECONDS} seconds..."
                )
                time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nOpenOps agent stopped gracefully.")


if __name__ == "__main__":
    main()
