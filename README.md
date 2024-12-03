# Internship Ordinatrum: Monitoring System with Dockerized Prometheus, Grafana, Node Exporter, Grok Exporter, and Telegraf

This project sets up a comprehensive monitoring system using Docker Compose, combining Prometheus, Grafana, Node Exporter, Grok Exporter, and Telegraf. It also includes an API to interact with Grafana and Prometheus, providing insights into device uptime, system performance, and potential issues.

## Features

- **System Resource Monitoring:** Uses Node Exporter and Telegraf to collect metrics from multiple nodes.
- **Visualization:** Grafana for real-time visualization and dashboards.
- **Log Parsing:** Grok Exporter parses logs and exports metrics to Prometheus.
- **Prometheus Integration:** Collects and stores time-series data for monitoring.
- **Custom API:** A Python FastAPI that interacts with Grafana and Prometheus to provide device monitoring and analysis.
- **Easy Deployment:** Docker Compose for easy setup and management of services.

## Prerequisites

- Docker (version 27.3.1, build ce12230)
- Docker Compose (version 1.29.2, build unknown)
- Python 3.13
- Conda 24.9.x or newer

## Installation

#### 1. Run [`.sh file`](install_and_run.sh) to clone the repository and start the docker-compose and the api. This also creates conda environment.

##### Make the Script Executable: If you haven’t done so already, run:

```
chmod +x install_and_run.sh
./install_and_run.sh
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
- **Response**:
    ```json
    [
        {
            "id": 1,
            "title": "Dashboard 1",
            "uri": "/dashboard/db/dashboard-1"
        },
        {
            "id": 2,
            "title": "Dashboard 2",
            "uri": "/dashboard/db/dashboard-2"
        }
    ]
    ```

#### `/prometheus/query`

- **Method**: `GET`
- **Description**: Query Prometheus data using the provided query and optional time range.
- **Query Parameters**:
    - `query`: PromQL query (required).
    - `start`: Start time of the query (optional, in ISO format or relative time, e.g., '10minute').
    - `end`: End time of the query (optional, default is 'now').
    - `step`: Step duration for data points (optional, e.g., '60s').
- **Response**:
    ```json
    {
        "status": "success",
        "data": {
            "result": [
                {
                    "metric": {"__name__": "up", "instance": "192.168.1.1"},
                    "values": [
                        [1635398640, "1"],
                        [1635398700, "0"]
                    ]
                }
            ]
        }
    }
    ```

#### `/prometheus/device_info`

- **Method**: `GET`
- **Description**: Fetch Prometheus data for specific device metrics over a time range.
- **Query Parameters**:
    - `start`: Start time for the data query (optional, default is '30minute').
    - `end`: End time for the data query (optional, default is 'now').
    - `metrics`: Dictionary of Prometheus queries (optional).
    - `step`: Step duration for data points (optional, default is '60s').
- **Response**:
    ```json
    [
        {
            "instance": "192.168.1.1",
            "metrics": [
                {
                    "timestamp": "2024-12-03 12:30:00",
                    "up": 1,
                    "cpu_usage": "0.03",
                    "memory_available": "50.1",
                    "disk_io": "0.002",
                    "network_errors": "0.0005"
                },
                {
                    "timestamp": "2024-12-03 12:31:00",
                    "up": 0,
                    "cpu_usage": "0.04",
                    "memory_available": "50.0",
                    "disk_io": "0.003",
                    "network_errors": "0.0006"
                }
            ],
            "uptime": {
                "total_time_seconds": 120,
                "uptime_time_seconds": 60,
                "uptime_percentage": 50
            }
        }
    ]
    ```
