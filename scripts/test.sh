#!/bin/bash
# Run all tests for CRM Digital FTE

echo "=============================================="
echo "🧪 CRM Digital FTE - Test Suite"
echo "=============================================="

# Activate virtual environment
source venv/bin/activate 2>/dev/null || true

# Run unit tests
echo -e "\n📝 Running Unit Tests..."
pytest tests/unit -v --cov=prototype --cov=backend --cov-report=html

# Run integration tests
echo -e "\n🔗 Running Integration Tests..."
pytest tests/integration -v

# Run API tests
echo -e "\n📡 Running API Tests..."
pytest tests/api -v

# Generate coverage report
echo -e "\n📊 Coverage Report:"
coverage report

echo ""
echo "=============================================="
echo "✅ Tests Complete!"
echo "=============================================="
echo ""
echo "📈 Coverage report: htmlcov/index.html"
echo ""
