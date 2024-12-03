import requests
from fastapi import FastAPI, Query
from datetime import datetime, timedelta
from keys import API_KEY

app = FastAPI()

GRAFANA_API_URL = "http://admin:admin@localhost:3000/api"
GRAFANA_API_KEY = f"Bearer {API_KEY}"
PROMETHEUS_API_URL = "http://localhost:9090/api/v1"

headers = {
    "Authorization": GRAFANA_API_KEY,
    "Content-Type": "application/json",
}

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

@app.get("/grafana/dashboards")
def get_dashboards():
    response = requests.get(f"{GRAFANA_API_URL}/search", headers=headers)
    return response.json()

@app.get("/prometheus/query")
def query_prometheus(query: str, start: str = None, end: str = None, step: str = None):
    params = {"query": query}
    if start and end and step:
        params.update({"start": start, "end": end, "step": step})
    response = requests.get(PROMETHEUS_API_URL, params=params)
    return response.json()

def analyze_data(prometheus_data):
    uptime = prometheus_data["data"]["result"]
    downtime_periods = []
    for data_point in uptime:
        timestamp, value = data_point["value"]
        if float(value) == 0:
            downtime_periods.append(timestamp)
    return {"downtime_periods": downtime_periods}

@app.get("/device/info")
def get_device_info():
    query = 'up{job="node_exporter"}'
    prometheus_response = query_prometheus(query)
    info = analyze_data(prometheus_response)
    return info

def calculate_start_time(n: int, period: str) -> str:
    """Helper function to calculate the start time based on the last n (minutes/days/months/years)"""
    now = datetime.utcnow()
    if period == 'minute':
        delta = timedelta(minutes=n)
    elif period == 'hour':
        delta = timedelta(hours=n)
    elif period == 'day':
        delta = timedelta(days=n)
    elif period == 'month':
        delta = timedelta(days=30*n)
    elif period == 'year':
        delta = timedelta(days=365*n)
    else:
        raise ValueError("Invalid period, must be one of: minute, day, month, year")

    start_time = now - delta
    return start_time.isoformat() + "Z"

@app.get("/prometheus/device_info")
def get_device_info(n: int = 60, metrics: dict = None, period: str = Query("minute", enum=["minute", "hour", "day", "month", "year"]), step: str = "60s"):
    step_ts = int(step[:-1])
    try:
        start_time = calculate_start_time(n, period)
    except ValueError as e:
        return {"error": str(e)}

    end_time = datetime.utcnow().isoformat() + "Z"

    if metrics is None: metrics = {
        "up":  "up",
        "cpu_usage": "rate(node_cpu_seconds_total{mode!='idle'}[5m])",
        "memory_available": "(node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100",
        "disk_io": "rate(node_disk_io_time_seconds_total[5m])",
        "network_errors": "rate(node_network_receive_errs_total[5m]) + rate(node_network_transmit_errs_total[5m])"
    }

    instance_data = {}

    for metric_name, query in metrics.items():
        params = {
            "query": query,
            "start": start_time,
            "end": end_time,
            "step": step
        }

        response = requests.get(f"{PROMETHEUS_API_URL}/query_range", params=params)
        if response.status_code != 200:
            return {"error": response.text}

        data = response.json()
        for result in data['data']['result']:
            instance = result['metric']['instance']
            
            if instance not in instance_data:
                instance_data[instance] = {
                    "metrics": {}
                }
            
            last_ts = 0
            for value in result['values']:
                timestamp = value[0]
                # print(timestamp, last_ts)
                # while timestamp-step_ts != last_ts:
                    
                metric_value = value[1]
                formatted_timestamp = format_date(timestamp)

                if formatted_timestamp not in instance_data[instance]["metrics"]:
                    instance_data[instance]["metrics"][formatted_timestamp] = {}

                instance_data[instance]["metrics"][formatted_timestamp][metric_name] = metric_value
                last_ts = timestamp

    final_data = []
    for instance, data in instance_data.items():
        instance_summary = {
            "instance": instance,
            "metrics": []
        }

        for timestamp, metrics_at_time in sorted(data["metrics"].items()):
            metrics_entry = {
                "timestamp": timestamp
            }
            metrics_entry.update(metrics_at_time)
            instance_summary["metrics"].append(metrics_entry)

        if "up" in metrics_at_time:
            uptime_data = [entry["up"] for entry in instance_summary["metrics"]]
            total_time = len(uptime_data) * step_ts
            uptime_time = sum([1 for entry in uptime_data if entry == "1"])
            uptime_percentage = (uptime_time / len(uptime_data)) * 100 if len(uptime_data) > 0 else 0

            instance_summary["uptime"] = {
                "total_time_seconds": total_time,
                "uptime_time_seconds": uptime_time * step_ts,
                "uptime_percentage": uptime_percentage
            }

        final_data.append(instance_summary)

    return final_data

def format_result(result_data: dict):
    return None

def format_date(date: float):
    return datetime.fromtimestamp(int(float(date))).isoformat() + "Z"
