import platform
import uuid

import psutil


def get_device_id():
    identity = f"{platform.node()}:{platform.system()}:{platform.machine()}"

    return str(uuid.uuid5(uuid.NAMESPACE_DNS, identity))


def collect_system_info():
    memory = psutil.virtual_memory()

    disk_path = (
        "C:\\"
        if platform.system() == "Windows"
        else "/"
    )

    disk = psutil.disk_usage(disk_path)

    return {
        "device_id": get_device_id(),
        "hostname": platform.node(),
        "os_name": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "cpu_cores": psutil.cpu_count(logical=True) or 1,
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory_total_bytes": memory.total,
        "memory_used_percent": memory.percent,
        "disk_total_bytes": disk.total,
        "disk_used_percent": disk.percent,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(collect_system_info(), indent=4))
