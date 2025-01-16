#!/bin/bash

# Check if port is in use
check_port() {
    if netstat -an | grep "LISTENING" | grep ":$1 " > /dev/null; then
        echo "Port $1 is in use"
        return 1
    fi
    return 0
}

# Check required ports
for port in 5434 9002 9003; do
    if ! check_port $port; then
        echo "Please free up port $port before running tests"
        exit 1
    fi
done

# Stop existing containers
docker-compose -f deploy/docker/docker-compose.test.yml down -v

# Start test environment
docker-compose -f deploy/docker/docker-compose.test.yml up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
for i in {1..30}; do
    if pg_isready -h localhost -p 5434 -U postgres > /dev/null 2>&1; then
        echo "PostgreSQL is ready"
        break
    fi
    echo "Waiting for PostgreSQL... ($i/30)"
    sleep 1
done

# Run tests
python -m pytest

# Clean up environment after tests
docker-compose -f deploy/docker/docker-compose.test.yml down -v