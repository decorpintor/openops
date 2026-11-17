from datetime import datetime, timezone

from pydantic import BaseModel, Field


class DeviceInventory(BaseModel):
    device_id: str
    hostname: str
    os_name: str
    os_version: str
    architecture: str
    cpu_cores: int = Field(ge=1)
    cpu_percent: float = Field(ge=0, le=100)
    memory_total_bytes: int = Field(gt=0)
    memory_used_percent: float = Field(ge=0, le=100)
    disk_total_bytes: int = Field(gt=0)
    disk_used_percent: float = Field(ge=0, le=100)


class DeviceRecord(DeviceInventory):
    registered_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_seen: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    status: str = "online"


class HeartbeatResponse(BaseModel):
    device_id: str
    status: str
    last_seen: datetime
    message: str = "Heartbeat received successfully"
