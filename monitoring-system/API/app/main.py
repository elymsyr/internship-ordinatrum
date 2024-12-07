import requests, re, logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from datetime import datetime
from helper import *

app = FastAPI()

@app.get("/grafana/dashboards", tags=["Grafana"])
def get_dashboards():
    """
    Fetch the list of Grafana dashboards.

    Returns:
        list: A list of Grafana dashboards in JSON format.
    """
    response = requests.get(f"{GRAFANA_API_URL}/search")
    return response.json()

@app.get("/grafana/dashboard/{uid}", tags=["Grafana"])
def get_dashboard_by_uid(uid: str):
    """
    Fetch a Grafana dashboard by UID.

    Args:
        uid (str): The UID of the Grafana dashboard.

    Returns:
        dict: JSON response with the dashboard details, including panels.
    """
    response = requests.get(f"{GRAFANA_API_URL}/dashboards/uid/{uid}")

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Dashboard with UID {uid} not found", "status_code": response.status_code}

@app.get("/prometheus/query", tags=["Prometheus"])
def query_prometheus(query: str = 'node_cpu_seconds_total{instance="node_exporter2:9100"}', start: str = '2024-12-01T00:00:00Z', end: str = 'now', step: str = '60s'):
    """
    Query Prometheus data using the provided query and optional time range.

    Args:
        query (str): PromQL query to fetch the metric data.
        start (str, optional): Start time of the query in ISO format or relative time (e.g., '10minute').
        end (str, optional): End time of the query in ISO format or relative time. Defaults to 'now'.
        step (str, optional): Step duration between data points in Prometheus (e.g., '60s').

    Returns:
        dict: The Prometheus query result in JSON format.
    """
    params = {"query": query}
    if end == "now":
        end = datetime.utcnow().isoformat() + "Z"
    params.update({"start": start, "end": end, "step": step})
    response = requests.get(f"{PROMETHEUS_API_URL}/query", params=params)
    return response.json()

@app.get("/prometheus/device_info", tags=["Prometheus"])
def get_device_info(
    start: str = "30minute",
    end: str = "now",
    metrics: dict = None,
    step: str = "60s"
):
    """
    Fetch Prometheus data for specific device metrics over a time range.

    Args:
        start (str, optional): Start time for the data query, in ISO format or relative time (e.g., '30minute').
            Defaults to '30minute'.
        end (str, optional): End time for the data query, in ISO format or relative time. Defaults to 'now'.
        metrics (dict, optional): Dictionary of Prometheus queries to fetch various metrics. 
            Defaults to a predefined set of common system metrics.
        step (str, optional): Step duration between data points in Prometheus, Seconds: s (e.g., 15s, 30s, 60s), Minutes: m (e.g., 1m, 5m, 10m), Hours: h (e.g., 1h, 6h, 12h), Days: d (e.g., 1d, 7d), Weeks: w (e.g., 1w, 2w). 
            Defaults to '60s'.

    Returns:
        list: A list of devices with their metrics and uptime information.
    """

    try:
        if re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", start):
            start_time = start
        else:
            start_time = parse_relative_time(start).isoformat() + "Z"
    except ValueError as e:
        return {"error": str(e)}

    if end == "now":
        end_time = datetime.utcnow().isoformat() + "Z"
    else:
        try:
            if re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", end):
                end_time = end
            else:
                end_time = parse_relative_time(end).isoformat() + "Z"
        except ValueError as e:
            return {"error": str(e)}

    start_timestamp = iso_to_unix_timestamp(start_time)
    end_timestamp = iso_to_unix_timestamp(end_time)
    
    step_duration_format = step[-1]
    step_timestamp = int(step[:-1])
    if step_duration_format in ['s', 'm', 'h', 'd', 'w']:
        if step_duration_format == 'm':
            step_timestamp *= 60
        elif step_duration_format == 'h':
            step_timestamp *= 3600
        elif step_duration_format == 'd':
            step_timestamp *= 3600 * 24
        elif step_duration_format == 'w':
            step_timestamp *= 3600 * 24 * 7
    else: raise ValueError("Invalid time format. Must be like '10s', '4w', '5d', etc.")

    expected_data = (end_timestamp-start_timestamp)/step_timestamp
    print(expected_data)

    if metrics is None:
        metrics = {
            "up": "up",
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
            "step": f"{step_timestamp}s"
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

            last_timestamp = None
            for value in result['values']:
                timestamp = value[0]
                if last_timestamp is None:
                    start_timestamp_follow = int(start_timestamp) + timestamp - int(timestamp)
                    while start_timestamp_follow+step_timestamp < timestamp:
                        start_timestamp_follow += step_timestamp
                        # print(start_timestamp_follow)
                        formatted_timestamp = format_date(start_timestamp_follow)
                        if formatted_timestamp not in instance_data[instance]["metrics"]:
                            instance_data[instance]["metrics"][formatted_timestamp] = {}
                        instance_data[instance]["metrics"][formatted_timestamp]['up'] = "0"

                while last_timestamp is not None and timestamp - step_timestamp != last_timestamp:
                    last_timestamp += step_timestamp
                    formatted_timestamp = format_date(last_timestamp)
                    if formatted_timestamp not in instance_data[instance]["metrics"]:
                        instance_data[instance]["metrics"][formatted_timestamp] = {}
                    instance_data[instance]["metrics"][formatted_timestamp]['up'] = "0"

                metric_value = value[1]
                formatted_timestamp = format_date(timestamp)

                if formatted_timestamp not in instance_data[instance]["metrics"]:
                    instance_data[instance]["metrics"][formatted_timestamp] = {}

                instance_data[instance]["metrics"][formatted_timestamp][metric_name] = metric_value
                last_timestamp = timestamp

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
            total_time = len(uptime_data) * step_timestamp
            uptime_time = sum([1 for entry in uptime_data if entry == "1"])
            uptime_percentage = (uptime_time / len(uptime_data)) * 100 if len(uptime_data) > 0 else 0

            instance_summary["uptime"] = {
                "total_time_seconds": total_time,
                "uptime_time_seconds": uptime_time * step_timestamp,
                "uptime_percentage": uptime_percentage
            }

        final_data.append(instance_summary)

    return final_data

@app.get("/")
def root():
    return {
        "message": "Welcome to the Monitoring API",
        "endpoints": {
            "/grafana/dashboards": "Fetch the list of Grafana dashboards.",
            "/prometheus/query": "Query Prometheus data with optional time range.",
            "/prometheus/device_info": "Fetch Prometheus data for specific device metrics over a time range."
        },
        "note": "For detailed information on each endpoint, refer to the documentation: github.com/elymsyr/internship-ordinatrum"
    }

alerts = []
active_connections = []

@app.post("/alerts/jobs", tags=["Alerts"])
async def receive_alert(request: Request):
    """
    Endpoint to receive an alert group via a POST request.
    
    This endpoint parses and validates the incoming JSON payload using the AlertGroup model,
    logs the received data, appends it to the alert list, and broadcasts it to all active WebSocket
    clients.

    - **alert_group**: A validated `AlertGroup` model containing the alert information.
    
    **Returns:**
    - A JSON response indicating the status and the alert group data.
    """
    # Parse and validate the incoming JSON data using the AlertGroup model
    payload = await request.json()
    alert_group = AlertGroup(**payload)  # Use Pydantic to validate and parse the data

    # Log the received alert payload
    logging.info(f"Received alert group: {alert_group}")

    # Append the parsed alert group to the alerts list
    alerts.append(alert_group)

    # Send the alert to all connected WebSocket clients
    for connection in active_connections:
        for alert in payload['alerts']:
            await connection.send_json(alert)
    
    return {"status": "Alert received", "data": alert_group.dict()}

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for receiving and sending messages related to alerts.
    
    This endpoint allows clients to establish a WebSocket connection and receive updates whenever
    a new alert is received. It also sends back any text data received from the client.

    - Clients can use this endpoint to receive alerts in real-time as they are posted to the `/alerts/jobs` endpoint.

    Example WebSocket interaction:
    - Client: Sends a message like "Hello Server"
    - Server: Responds with "Message text: Hello Server"
    
    The WebSocket connection is maintained until the client disconnects.
    """
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text: {data}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)