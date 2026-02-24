#!/bin/bash
# Docker verification and testing script

set -e

echo "🔍 RAG Service - Docker Verification"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Docker installation
echo "Test 1: Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓${NC} Docker installed: $DOCKER_VERSION"
else
    echo -e "${RED}✗${NC} Docker not found"
    exit 1
fi
echo ""

# Test 2: Docker Compose installation
echo "Test 2: Checking Docker Compose installation..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}✓${NC} Docker Compose installed: $COMPOSE_VERSION"
else
    echo -e "${RED}✗${NC} Docker Compose not found"
    exit 1
fi
echo ""

# Test 3: .env file
echo "Test 3: Checking .env file..."
if [ -f .env ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    
    # Check for required variables
    REQUIRED_VARS=("OPENAI_API_KEY" "SUPABASE_URL" "SUPABASE_KEY" "JWT_SECRET_KEY")
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^$var=" .env; then
            echo -e "${GREEN}✓${NC} $var is configured"
        else
            echo -e "${YELLOW}⚠${NC} $var might not be configured"
        fi
    done
else
    echo -e "${RED}✗${NC} .env file not found"
    echo -e "${YELLOW}Please create .env from .env.example${NC}"
    exit 1
fi
echo ""

# Test 4: Docker images
echo "Test 4: Building Docker images..."
docker-compose build 2>&1 | tail -5
echo -e "${GREEN}✓${NC} Images built successfully"
echo ""

# Test 5: Start containers
echo "Test 5: Starting containers..."
docker-compose up -d
echo -e "${GREEN}✓${NC} Containers started"
sleep 3
echo ""

# Test 6: Container status
echo "Test 6: Checking container status..."
docker-compose ps
echo ""

# Test 7: Backend health check
echo "Test 7: Checking backend health..."
MAX_ATTEMPTS=10
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend is healthy"
        BACKEND_HEALTHY=true
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
        echo "  Attempt $ATTEMPT/$MAX_ATTEMPTS, waiting..."
        sleep 2
    fi
done

if [ -z "$BACKEND_HEALTHY" ]; then
    echo -e "${RED}✗${NC} Backend health check failed"
    echo "Logs:"
    docker-compose logs backend | tail -20
else
    echo -e "${GREEN}✓${NC} Backend is running at http://localhost:8000"
fi
echo ""

# Test 8: API accessibility
echo "Test 8: Testing API endpoints..."
if [ "$BACKEND_HEALTHY" = true ]; then
    # Test root endpoint
    RESPONSE=$(curl -s http://localhost:8000/ | jq -r '.status' 2>/dev/null || echo "")
    if [ "$RESPONSE" = "healthy" ]; then
        echo -e "${GREEN}✓${NC} API root endpoint working"
    else
        echo -e "${YELLOW}⚠${NC} API root endpoint response: $RESPONSE"
    fi
    
    # Test health endpoint
    HEALTH=$(curl -s http://localhost:8000/health | jq -r '.status' 2>/dev/null || echo "")
    if [ "$HEALTH" = "healthy" ]; then
        echo -e "${GREEN}✓${NC} Health endpoint working"
    else
        echo -e "${YELLOW}⚠${NC} Health endpoint response: $HEALTH"
    fi
    
    # Test docs endpoint
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓${NC} API documentation available at http://localhost:8000/docs"
    else
        echo -e "${YELLOW}⚠${NC} API docs returned HTTP $HTTP_CODE"
    fi
fi
echo ""

# Test 9: Frontend check
echo "Test 9: Checking frontend..."
MAX_ATTEMPTS=10
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
        echo -e "${GREEN}✓${NC} Frontend is running at http://localhost:8501"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
        echo "  Attempt $ATTEMPT/$MAX_ATTEMPTS, waiting..."
        sleep 2
    fi
done
echo ""

# Test 10: Logs check
echo "Test 10: Checking for errors in logs..."
BACKEND_ERRORS=$(docker-compose logs backend | grep -i "error" | wc -l || echo "0")
if [ "$BACKEND_ERRORS" = "0" ]; then
    echo -e "${GREEN}✓${NC} No errors in backend logs"
else
    echo -e "${YELLOW}⚠${NC} Found $BACKEND_ERRORS errors in backend logs"
    docker-compose logs backend | grep -i "error" | head -3
fi
echo ""

# Summary
echo "===================================="
echo -e "${GREEN}✓ Docker Verification Complete!${NC}"
echo "===================================="
echo ""
echo "Services Status:"
docker-compose ps
echo ""
echo "Access Points:"
echo "  API:              http://localhost:8000"
echo "  API Docs:         http://localhost:8000/docs"
echo "  Frontend:         http://localhost:8501"
echo "  Health Check:     http://localhost:8000/health"
echo ""
echo "Useful Commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart services: docker-compose restart"
echo ""
