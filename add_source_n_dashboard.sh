#!/bin/bash

set -e

GRAFANA_URL="http://localhost:3000"
GRAFANA_ADMIN_USER="admin"
GRAFANA_ADMIN_PASSWORD="admin"

PROMETHEUS_URL="http://prometheus:9090"
DATASOURCE_NAME="Prometheus"

GRAFANA_COOKIE=$(curl -s -X POST -d "user=${GRAFANA_ADMIN_USER}&password=${GRAFANA_ADMIN_PASSWORD}" -c cookies.txt ${GRAFANA_URL}/login)

curl -s -X POST -H "Content-Type: application/json" \
    -b cookies.txt \
    -d '{
          "name": "'${DATASOURCE_NAME}'",
          "type": "prometheus",
          "url": "'${PROMETHEUS_URL}'",
          "access": "proxy",
          "isDefault": true
        }' \
    ${GRAFANA_URL}/api/datasources

echo "Uploading Grafana dashboard..."

DASHBOARD_FILE="monitoring-system/dashboards/dashboard1.json"

if [ ! -f "$DASHBOARD_FILE" ]; then
    echo "Dashboard file not found: $DASHBOARD_FILE"
    exit 1
fi

DASHBOARD_JSON=$(cat $DASHBOARD_FILE)

curl -s -X POST -H "Content-Type: application/json" \
    -b cookies.txt \
    -d '{
          "dashboard": '"$DASHBOARD_JSON"',
          "overwrite": true
        }' \
    ${GRAFANA_URL}/api/dashboards/db

rm cookies.txt

echo "Dashboards ready!"
