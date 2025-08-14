#!/bin/bash

echo "🧪 AI Research Agent Test Runner"
echo "================================"

if [ -z "$1" ]; then
    echo "Running all tests..."
    cd tests
    python3 run_tests.py all
else
    echo "Running $1 tests..."
    cd tests
    python3 run_tests.py "$1"
fi

echo ""
echo "Tests completed!" 