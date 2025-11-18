#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Starting FastAPI Auth Server Tests..."
echo "======================================"

# Kill any existing server on port 8000
echo "Cleaning up any existing server..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start the server in the background
echo "Starting server on http://localhost:8000..."
python3 main.py > server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to be ready..."
sleep 3

# Check if server is running
if ! curl -s http://localhost:8000 > /dev/null; then
    echo -e "${RED}Failed to start server${NC}"
    cat server.log
    exit 1
fi

echo -e "${GREEN}Server started successfully!${NC}"
echo ""

# Generate a random username for testing
TEST_USERNAME="testuser$(date +%s)"

# Run newman tests
echo "Running Newman tests..."
echo "======================================"
newman run \
    --env-var baseUrl="http://localhost:8000" \
    --env-var username="$TEST_USERNAME" \
    https://raw.githubusercontent.com/UXGorilla/hiring-backend/main/collection.json

NEWMAN_EXIT_CODE=$?

# Cleanup
echo ""
echo "Cleaning up..."
kill $SERVER_PID 2>/dev/null
rm -f server.log

if [ $NEWMAN_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed${NC}"
    exit 1
fi