#!/bin/bash
# Setup script for CRM Digital FTE

echo "=============================================="
echo "🏗️  CRM Digital FTE - Setup Script"
echo "=============================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}Checking Python...${NC}"
python3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}Python 3.11+ is required${NC}"
    exit 1
fi

# Check Node.js
echo -e "${BLUE}Checking Node.js...${NC}"
node --version
if [ $? -ne 0 ]; then
    echo -e "${RED}Node.js 18+ is required${NC}"
    exit 1
fi

# Check Docker
echo -e "${BLUE}Checking Docker...${NC}"
docker --version
if [ $? -ne 0 ]; then
    echo -e "${RED}Docker is required${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies
echo -e "${BLUE}Installing frontend dependencies...${NC}"
cd frontend
npm install
cd ..

# Create .env file
echo -e "${BLUE}Creating .env file...${NC}"
if [ ! -f prototype/.env ]; then
    cp prototype/.env.example prototype/.env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${RED}⚠️  Please edit prototype/.env with your credentials${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Start Docker services
echo -e "${BLUE}Starting Docker services (Kafka, Zookeeper)...${NC}"
cd kafka
docker-compose up -d
cd ..

# Wait for Kafka to be ready
echo -e "${BLUE}Waiting for Kafka to be ready...${NC}"
sleep 10

# Create database
echo -e "${BLUE}Creating PostgreSQL database...${NC}"
read -p "Enter PostgreSQL username (default: postgres): " DB_USER
DB_USER=${DB_USER:-postgres}
psql -U $DB_USER -c "CREATE DATABASE crm_digital_fte;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database created${NC}"
    
    # Run schema
    echo -e "${BLUE}Running database schema...${NC}"
    psql -U $DB_USER -d crm_digital_fte -f database/schema.sql
    echo -e "${GREEN}✓ Schema applied${NC}"
else
    echo -e "${RED}⚠️  Database creation failed. Please create manually:${NC}"
    echo "  psql -U postgres -c 'CREATE DATABASE crm_digital_fte;'"
    echo "  psql -U postgres -d crm_digital_fte -f database/schema.sql"
fi

echo ""
echo "=============================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=============================================="
echo ""
echo "📋 Next Steps:"
echo "   1. Edit prototype/.env with your credentials"
echo "   2. Start the API server:"
echo "      source venv/bin/activate"
echo "      cd prototype && python main.py"
echo ""
echo "   3. Start the Kafka worker:"
echo "      python kafka/worker.py"
echo ""
echo "   4. Start the frontend:"
echo "      cd frontend && npm run dev"
echo ""
echo "📚 Documentation:"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Frontend: http://localhost:3000"
echo "   - Kafka UI: http://localhost:8080"
echo ""
