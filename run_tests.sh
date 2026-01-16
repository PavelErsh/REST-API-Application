#!/bin/bash

# Script to run tests with coverage

echo "Installing test dependencies..."
pip install -q -r requirements-test.txt

echo ""
echo "Running tests with pytest..."
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

echo ""
echo "Test coverage report generated in htmlcov/"
echo "To view: open htmlcov/index.html"
