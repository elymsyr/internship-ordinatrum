# Internship Ordinatrum: Monitoring System with Dockerized Prometheus, Grafana, Node Exporter, Grok Exporter, and Telegraf

This project sets up a comprehensive monitoring system using Docker Compose, combining Prometheus, Grafana, Node Exporter, Grok Exporter, and Telegraf. It also includes an API to interact with Grafana and Prometheus, providing insights into device uptime, system performance, and potential issues.
<div style="display: flex; justify-content: center; align-items: center; height: fit; flex-direction: column; text-align: center;">
    <a href="monitoring-system/API/app/alert_api_test.html" style="color: inherit;">
        <h4>Raw Alert Notification with Embedded Panels</h4>
        <img src="alert.png" width="550" alt="Raw Alert Notification with Embedded Panels">
    </a>
</div>

## Features

- **System Resource Monitoring:** Uses Node Exporter and Telegraf to collect metrics from multiple nodes.
- **Visualization:** Grafana for real-time visualization and dashboards. API and WebSockets to interpret the data or alerts and visualize in real-time.
- **Log Parsing:** Grok Exporter parses logs and exports metrics to Prometheus.
- **Prometheus Integration:** Collects and stores time-series data for monitoring.
- **Custom API:** A Python FastAPI that interacts with Grafana and Prometheus to provide device monitoring and analysis.
- **Easy Deployment:** Docker Compose for easy setup and management of services.

## Prerequisites

- Docker (version 27.3.1, build ce12230)
- Docker Compose (version 1.29.2, build unknown)

## Installation

#### 1. Run [`.sh file`](install_and_run.sh) to clone the repository and start the docker-compose with the api.

##### Make the Script Executable: If you haven’t done so already, run:

```
chmod +x install_and_run.sh
./install_and_run.sh
```
```bash
#!/bin/bash

set -e

echo "Cloning the repository..."
git clone https://github.com/elymsyr/internship-ordinatrum.git
cd internship-ordinatrum/monitoring-system

# SET YOUR SMTP SETTINGS

echo "SMTP_USER=myuser.com" > .env
echo "SMTP_PASSWORD=mypassword" >> .env
echo "SMTP_HOST=smtp.example.com:587" >> .env
echo "SMTP_FROM_ADRESS=example@gmail.com" >> .env

echo "Building and starting Docker containers..."
docker-compose up --build -d

echo "Waiting for services to start..."
sleep 10
docker-compose ps

echo "Docker containers are running. You can access Grafana at http://localhost:3000"

echo "To access Grafana, use the default login credentials:"
echo "Username: admin"
echo "Password: admin"

# Wait a couple of minutes until the alert is triggered. You will see the notification here.
xdg-open monitoring-system/API/app/alert_api_test.html

xdg-open http://localhost:3000/
xdg-open http://localhost:9090/
xdg-open http://localhost:9093/
xdg-open http://0.0.0.0:8000/docs


echo "Installation and setup completed!"

```

#### 2. Run [`.sh file`](add_source_n_dashboard.sh) to add Prometheus as the data source and import the [`dashboard1`](monitoring-system/dashboards/dashboard1.json) to Grafana.

##### Make the Script Executable: If you haven’t done so already, run:

```
chmod +x add_source_n_dashboard.sh.sh
./add_source_n_dashboard.sh.sh
```

*If you get any error related to the data source uid, be sure that the data source uid is same with the one in the dashboard json files. Create a new datasource with hand and find data source uid by checking the new data source's JSON. Change the data source uid in the dashboard1.json and dashboard2.json files. Import files to Grafana again.*


## API Documentation

### Endpoints

#### `/grafana/dashboards`

- **Method**: `GET`
- **Description**: Fetch the list of Grafana dashboards.

#### `/prometheus/query`

- **Method**: `GET`
- **Description**: Query Prometheus data using the provided query and optional time range.
- **Query Parameters**:
    - `query`: PromQL query (required).
    - `start`: Start time of the query (optional, in ISO format or relative time, e.g., '10minute').
    - `end`: End time of the query (optional, default is 'now').
    - `step`: Step duration for data points (optional, e.g., '60s').

#### `/prometheus/device_info`

- **Method**: `GET`
- **Description**: Fetch Prometheus data for specific device metrics over a time range.
- **Query Parameters**:
    - `start`: Start time for the data query (optional, default is '30minute').
    - `end`: End time for the data query (optional, default is 'now').
    - `metrics`: Dictionary of Prometheus queries (optional).
    - `step`: Step duration for data points (optional, default is '60s').

#### `/alerts/jobs`
- **Method**: `POST`
- **Description**: Receive an alert group and broadcast it to all connected WebSocket clients. The payload is validated using the AlertGroup model, logged, and added to the list of alerts.
- **Request Body**:
    ```python
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
            extra = "allow"
        @root_validator(pre=True)
        def capture_extra_fields(cls, values):
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
            extra = "allow"
        @root_validator(pre=True)
        def capture_extra_fields(cls, values):
            extra_data = {key: value for key, value in values.items() if key not in cls.__fields__}
            if extra_data:
                values['extra_fields'] = extra_data
            return values
    ```

#### `/ws/alerts`
- **Method**: `WebSocket`
- **Description**: WebSocket endpoint for clients to receive real-time alerts. When an alert is posted via /alerts/jobs, it is broadcast to all connected WebSocket clients. The endpoint also allows clients to send messages that the server will echo back.
