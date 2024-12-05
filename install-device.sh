#!/bin/bash

set -e

echo "Cloning the repository..."
git clone https://github.com/elymsyr/internship-ordinatrum.git
cd internship-ordinatrum/monitoring-system

echo "Building and starting Docker containers..."
docker-compose -f docker-compose-device.yml up -d

echo "Waiting for services to start..."
sleep 3
docker-compose -f docker-compose-device.yml ps

echo "Installation and setup completed!"
