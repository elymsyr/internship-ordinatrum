#!/bin/bash

set -e

echo "Cloning the repository..."
git clone https://github.com/elymsyr/internship-ordinatrum.git
cd internship-ordinatrum/monitoring-system

# SET YOUR SMTP SETTINGS IF YOU USE MAIL NOTIFICATION

echo "SMTP_USER=myuser.com" > .env
echo "SMTP_PASSWORD=mypassword" >> .env
echo "SMTP_HOST=smtp.example.com:587" >> .env
echo "SMTP_FROM_ADRESS=example@gmail.com" >> .env

docker network create monitoring

echo "Building and starting Docker containers..."
docker-compose -f docker-compose-main.yml up -d

echo "Waiting for services to start..."
sleep 5
docker-compose -f docker-compose-main.yml ps

echo "Docker containers are running. You can access Grafana at http://localhost:3000"

echo "To access Grafana, use the default login credentials:"
echo "Username: admin"
echo "Password: admin"

xdg-open API/app/alert_api_test.html

xdg-open http://localhost:3000/
xdg-open http://localhost:9090/
xdg-open http://localhost:9093/
xdg-open http://0.0.0.0:8000/docs

docker logs fastapi
echo "Installation and setup completed!"
