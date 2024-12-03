# Internship Ordinatrum: Monitoring System with Dockerized Prometheus, Grafana, Node Exporter, Grok Exporter, and Telegraf

This project sets up a comprehensive monitoring system using Docker Compose, combining Prometheus, Grafana, Node Exporter, Grok Exporter, and Telegraf. It also includes an API to interact with Grafana and Prometheus, providing insights into device uptime, system performance, and potential issues.

## Features

- *System Resource Monitoring:* Uses Node Exporter and Telegraf to collect metrics from multiple nodes.
- *Visualization:* Grafana for real-time visualization and dashboards.
- *Log Parsing:* Grok Exporter parses logs and exports metrics to Prometheus.
- *Prometheus Integration:* Collects and stores time-series data for monitoring.
- *Custom API:* A Python FastAPI that interacts with Grafana and Prometheus to provide device monitoring and analysis.
- *Easy Deployment:* Docker Compose for easy setup and management of services.

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
Run the Script: Execute the script:
```
```
./install_and_run.sh
```

#### 2. Run [`.sh file`](add_source_n_dashboard.sh) to add Prometheus as the data source and the [`dashboard1`](monitoring-system/dashboards/dashboard1.json) to Grafana.

##### Make the Script Executable: If you haven’t done so already, run:

```
chmod +x add_source_n_dashboard.sh.sh
Run the Script: Execute the script:
```
```
./add_source_n_dashboard.sh.sh
```

##### Be sure that the data source uid is same with the one in the dashboard json files.
