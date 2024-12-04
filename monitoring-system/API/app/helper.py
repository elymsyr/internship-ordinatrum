# from keys import API_KEY
import re
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, root_validator
from typing import Union, Any, Dict, List

GRAFANA_API_URL = "http://admin:admin@localhost:3000/api"
# GRAFANA_API_KEY = f"Bearer {API_KEY}"
PROMETHEUS_API_URL = "http://localhost:9090/api/v1"

# headers = {
#     "Authorization": GRAFANA_API_KEY,
#     "Content-Type": "application/json",
# }

metrics = {
    'system_metrics': {
        'cpu': [
            'node_cpu_seconds_total',  # Total CPU time spent in different modes (user, system, idle, etc.)
            'node_cpu_seconds_user',   # Time spent in user mode
            'node_cpu_seconds_system', # Time spent in system mode
            'node_cpu_seconds_idle',   # Time spent idle
            'node_cpu_seconds_iowait', # Time spent waiting for I/O
        ],
        'memory': [
            'node_memory_MemTotal_bytes',  # Total memory available in the system
            'node_memory_MemFree_bytes',   # Free memory
            'node_memory_Buffers_bytes',   # Memory used by buffers
            'node_memory_Cached_bytes',    # Memory used for caching files
            'node_memory_SwapTotal_bytes', # Total swap memory
            'node_memory_SwapFree_bytes'   # Free swap memory
        ],
        'disk_io': [
            'node_disk_io_now',            # Number of I/Os currently in progress
            'node_disk_io_time_seconds',   # Total time spent doing I/O operations
            'node_disk_read_bytes_total',  # Total number of bytes read
            'node_disk_written_bytes_total' # Total number of bytes written
        ],
        'filesystem': [
            'node_filesystem_size_bytes',  # Total size of the filesystem
            'node_filesystem_free_bytes',  # Free space on the filesystem
            'node_filesystem_avail_bytes', # Space available for unprivileged users
            'node_filesystem_files_free'   # Free inodes
        ],
        'network': [
            'node_network_receive_bytes_total',   # Total number of bytes received
            'node_network_transmit_bytes_total',  # Total number of bytes transmitted
            'node_network_receive_errs_total',    # Total receive errors
            'node_network_transmit_errs_total',   # Total transmit errors
            'node_network_receive_packets_total', # Total packets received
            'node_network_transmit_packets_total' # Total packets transmitted
        ]
    },
    'hardware_metrics': {
        'temperature': [
            'node_hwmon_temp_celsius' # Current hardware temperature (requires lm-sensors or other monitoring tools)
        ],
        'fan_speed': [
            'node_hwmon_fan_speed_rpm' # Current fan speed in RPM
        ],
        'power_supply': [
            'node_hwmon_power_watts'   # Current power usage in watts
        ]
    }
}

class Alert(BaseModel):
    status: str
    starts_at: datetime = Field(alias="startsAt")
    ends_at: datetime = Field(alias="endsAt")
    generator_url: str = Field(alias="generatorURL")
    annotations: Dict[str, str]
    labels: Dict[str, str]
    fingerprint: str
    extra_fields: Dict[str, Any] = {}

    class Config:
        extra = "allow"  # Automatically allows extra fields

    @root_validator(pre=True)
    def capture_extra_fields(cls, values):
        # Capture any extra fields that are not explicitly defined in the model
        extra_data = {key: value for key, value in values.items() if key not in cls.__fields__}
        if extra_data:
            values['extra_fields'] = extra_data
        return values


class AlertGroup(BaseModel):
    receiver: str
    status: str
    external_url: str = Field(alias="externalURL")
    version: str
    group_key: str = Field(alias="groupKey")
    truncated_alerts: int = Field(alias="truncatedAlerts", default=0)
    group_labels: Dict[str, str] = Field(alias="groupLabels")
    common_annotations: Dict[str, str] = Field(alias="commonAnnotations")
    common_labels: Dict[str, str] = Field(alias="commonLabels")
    alerts: List[Alert]
    extra_fields: Dict[str, Any] = {}

    class Config:
        extra = "allow"  # Automatically allows extra fields

    @root_validator(pre=True)
    def capture_extra_fields(cls, values):
        # Capture any extra fields that are not explicitly defined in the model
        extra_data = {key: value for key, value in values.items() if key not in cls.__fields__}
        if extra_data:
            values['extra_fields'] = extra_data
        return values

def analyze_data(prometheus_data):
    uptime = prometheus_data["data"]["result"]
    downtime_periods = []
    for data_point in uptime:
        timestamp, value = data_point["value"]
        if float(value) == 0:
            downtime_periods.append(timestamp)
    return {"downtime_periods": downtime_periods}

def parse_relative_time(relative_time: str) -> datetime:
    """Parse relative time like '10minute', '5hour', etc., and return the corresponding datetime."""
    pattern = r"(\d+)(minute|hour|day|month|year)"
    match = re.match(pattern, relative_time)

    if not match:
        raise ValueError("Invalid time format. Must be like '10minute', '5hour', etc.")

    value, unit = match.groups()
    value = int(value)

    now = datetime.utcnow()

    if unit == 'minute':
        delta = timedelta(minutes=value)
    elif unit == 'hour':
        delta = timedelta(hours=value)
    elif unit == 'day':
        delta = timedelta(days=value)
    elif unit == 'month':
        delta = timedelta(days=30 * value)
    elif unit == 'year':
        delta = timedelta(days=365 * value)
    else:
        raise ValueError("Invalid period unit, must be one of: minute, hour, day, month, year")

    return now - delta

def iso_to_unix_timestamp(iso_timestamp: str) -> float:
    dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    unix_timestamp = dt.timestamp()
    return unix_timestamp

def format_date(date: float):
    return datetime.fromtimestamp(int(float(date))).isoformat() + "Z"
