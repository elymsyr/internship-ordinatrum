#!/bin/bash

set -e

echo "Cloning the repository..."
git clone https://github.com/elymsyr/internship-ordinatrum.git
cd monitoring-system

echo "Building and starting Docker containers..."
docker-compose up --build -d

echo "Waiting for services to start..."
sleep 10
docker-compose up ps

echo "Docker containers are running. You can access Grafana at http://localhost:3000"

echo "To access Grafana, use the default login credentials:"
echo "Username: admin"
echo "Password: admin"

cd ../API
uvicorn main:app --reload
sleep 5

echo "API is running. You can interact with the system via the FastAPI server (http://localhost:8000)."

echo "Installation and setup completed!"
