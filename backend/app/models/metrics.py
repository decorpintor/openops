from datetime import datetime, timezone

from pydantic import BaseModel, Field


class DeviceMetricCreate(BaseModel):
    cpu_percent: float = Field(ge=0, le=100)
    memory_used_percent: float = Field(ge=0, le=100)
    disk_used_percent: float = Field(ge=0, le=100)


class DeviceMetricRecord(DeviceMetricCreate):
    metric_id: int
    device_id: str
    collected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
