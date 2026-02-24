# Docker & Deployment Guide

## Overview

This RAG Service uses Docker for containerization with:
- **Backend**: FastAPI application (Port 8000)
- **Frontend**: Streamlit application (Port 8501)
- **Orchestration**: Docker Compose for local development and production

---

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git
- Bash/PowerShell (depending on OS)

### Installation

**Windows**:
```powershell
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Docker Desktop includes Docker Compose
```

**Linux**:
```bash
# Install Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Add user to docker group (optional)
sudo usermod -aG docker $USER
```

**macOS**:
```bash
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
```

---

## Quick Start - Development

### 1. Setup Environment

```bash
# Copy and configure environment file
cp .env.example .env

# Edit .env with your credentials
# OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY, etc.
```

### 2. Create Required Directories

```bash
mkdir -p documents logs
```

### 3. Build Images

```bash
docker-compose build
```

### 4. Start Services

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 5. Access Services

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:8501
- **Health Check**: http://localhost:8000/health

### 6. Stop Services

```bash
docker-compose down

# Remove volumes (deletes data)
docker-compose down -v
```

---

## Common Docker Commands

### View Running Containers
```bash
docker-compose ps
```

### View Service Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```

### Execute Command in Container
```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend bash

# Run tests
docker-compose exec backend pytest
```

### Rebuild Images
```bash
# Rebuild without cache
docker-compose build --no-cache

# Rebuild specific service
docker-compose build --no-cache backend
```

### Check Container Health
```bash
docker-compose ps
# STATUS column shows: Up (healthy) or Up (unhealthy)
```

### View Resource Usage
```bash
docker stats
```

---

## Production Deployment

### 1. Using Production Compose File

```bash
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Configuration for Production

Create `.env.prod`:
```env
# Production settings
OPENAI_API_KEY=your_production_key
SUPABASE_URL=your_production_url
SUPABASE_KEY=your_production_key
JWT_SECRET_KEY=strong_secret_key_here
EMAILS="admin@example.com"

# Resource settings
WORKERS=4
MAX_POOL_SIZE=20
```

### 3. SSL/TLS Setup

```bash
# Generate SSL certificates
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365

# Update nginx.conf with your domain
# Uncomment SSL section and point to certificates
```

### 4. Health Monitoring

```bash
# Check if services are healthy
docker-compose ps

# Check logs for errors
docker-compose logs --tail=50

# Execute health checks
curl http://localhost:8000/health
curl http://localhost:8501/_stcore/health
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Missing .env file
# 2. Port already in use
# 3. Insufficient resources
```

### Port Already in Use
```bash
# Change ports in docker-compose.yml
# Example: ports: ["9000:8000"]

# Or find and kill process using port
# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Linux
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Performance Issues
```bash
# Check container resource usage
docker stats

# Check available disk space
df -h

# Limit container resources in docker-compose.yml:
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

### Database Connection Issues
```bash
# Verify Supabase credentials in .env
# Check network connectivity
docker-compose exec backend curl -I $SUPABASE_URL

# Check database is accessible
docker-compose exec backend python -c "from config import settings; print(settings.supabase_url)"
```

### API Not Responding
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

---

## Docker Image Management

### View Images
```bash
docker images | grep rag
```

### Remove Images
```bash
# Remove specific image
docker rmi rag-service-backend

# Remove all unused images
docker image prune
```

### Push to Registry

#### Docker Hub
```bash
# Tag image
docker tag rag-service-backend:latest yourusername/rag-backend:latest

# Login to Docker Hub
docker login

# Push image
docker push yourusername/rag-backend:latest
```

#### Azure Container Registry
```bash
# Login
az acr login --name yourregistry

# Tag image
docker tag rag-service-backend:latest yourregistry.azurecr.io/rag-backend:latest

# Push
docker push yourregistry.azurecr.io/rag-backend:latest
```

---

## Environment Variables

### Development (.env)
```env
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://...
SUPABASE_KEY=...
JWT_SECRET_KEY=your-secret-key
# ... more variables
```

### Production (.env.prod)
```env
# Same as development but with production values
# Ensure JWT_SECRET_KEY is strong
# Ensure all credentials are from production services
```

---

## Volumes & Persistence

### Mounted Directories
- `./documents/` → `/app/documents` - Document storage
- `./logs/` → `/app/logs` - Application logs

### Preserve Data
```bash
# Backup documents
docker cp rag-backend:/app/documents ./backup/

# Restore documents
docker cp ./backup/documents rag-backend:/app/
```

---

## Building for Different Architectures

### Multi-architecture Build
```bash
# Build for ARM64 (Apple Silicon, Raspberry Pi)
docker buildx build --platform linux/arm64 -t rag-backend:arm64 .

# Build for AMD64 (Standard Intel/AMD)
docker buildx build --platform linux/amd64 -t rag-backend:amd64 .

# Build for both
docker buildx build --platform linux/amd64,linux/arm64 -t rag-backend:latest .
```

---

## Docker Secrets (for Production)

```bash
# Create secrets
echo "your-secret-key" | docker secret create jwt_secret -

# Use in compose file
secrets:
  jwt_secret:
    external: true

# Reference in service
environment:
  JWT_SECRET_KEY: /run/secrets/jwt_secret
```

---

## Next Steps

1. ✅ Docker files created
2. ⏭️ Setup CI/CD with GitHub Actions
3. ⏭️ Deploy to Azure Container Instances
4. ⏭️ Setup monitoring and logging

For deployment to Azure, see [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md)
