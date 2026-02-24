# Deployment Guide

## Production Deployment Options

### Option 1: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  rag-api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

Deploy:
```bash
docker-compose up -d
```

### Option 2: Cloud Deployment (AWS EC2)

1. **Launch EC2 Instance**
   - Ubuntu 22.04 LTS
   - t3.medium or larger
   - Open port 8000 in security group

2. **Setup Server**
```bash
# SSH into server
ssh -i your-key.pem ubuntu@your-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv -y

# Clone/upload your code
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure systemd service**

Create `/etc/systemd/system/rag-api.service`:

```ini
[Unit]
Description=RAG Chatbot API
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/rag-service
Environment="PATH=/home/ubuntu/rag-service/venv/bin"
EnvironmentFile=/home/ubuntu/rag-service/.env
ExecStart=/home/ubuntu/rag-service/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable rag-api
sudo systemctl start rag-api
sudo systemctl status rag-api
```

4. **Setup Nginx (Optional)**

Install Nginx:
```bash
sudo apt install nginx -y
```

Configure `/etc/nginx/sites-available/rag-api`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/rag-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: Cloud Platforms

#### Railway.app
1. Create account at railway.app
2. New Project > Deploy from GitHub
3. Add environment variables
4. Deploy

#### Render.com
1. Create account at render.com
2. New Web Service
3. Connect repository
4. Add environment variables
5. Deploy

#### Heroku
```bash
# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
heroku config:set OPENAI_API_KEY=your-key
heroku config:set SUPABASE_URL=your-url
# ... set other env vars
```

## Production Configuration

### 1. Environment Variables

```env
# Production settings
OPENAI_API_KEY=your-key
SUPABASE_URL=your-url
SUPABASE_KEY=your-key
DOCUMENTS_PATH=/app/documents

# Optimization
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Model selection
EMBEDDING_MODEL=text-embedding-3-large
CHAT_MODEL=gpt-4-turbo-preview
```

### 2. CORS Configuration

In `main.py`, update CORS for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting

Install rate limiting:
```bash
pip install slowapi
```

Add to `main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest):
    # ... existing code
```

### 4. Logging

Configure structured logging in production:

```python
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### 5. Health Checks

The `/health` endpoint can be used for:
- Load balancer health checks
- Kubernetes liveness probes
- Monitoring systems

### 6. Monitoring

#### Application Performance Monitoring

Use services like:
- Sentry for error tracking
- DataDog for metrics
- New Relic for APM

Example Sentry integration:
```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Rotate API keys regularly
- [ ] Set proper CORS origins
- [ ] Implement rate limiting
- [ ] Use environment variables for secrets
- [ ] Enable firewall rules
- [ ] Keep dependencies updated
- [ ] Use strong Supabase passwords
- [ ] Implement API authentication (if needed)
- [ ] Regular security audits

## Scaling Considerations

### Horizontal Scaling
- Run multiple instances behind a load balancer
- Use managed services (AWS ELB, etc.)
- Consider container orchestration (Kubernetes)

### Performance Optimization
- Cache frequently asked questions
- Use Redis for session management
- Optimize chunk sizes for your use case
- Consider using smaller models for faster responses

### Database Optimization
- Monitor Supabase performance
- Adjust IVFFlat index parameters
- Consider dedicated Supabase instance
- Implement connection pooling

## Cost Optimization

1. **OpenAI Costs**
   - Use `text-embedding-3-small` if acceptable
   - Use `gpt-3.5-turbo` instead of GPT-4 for cost savings
   - Implement caching for common queries

2. **Supabase Costs**
   - Monitor database size
   - Regular cleanup of old embeddings
   - Consider upgrading to Pro for better performance

3. **Infrastructure Costs**
   - Right-size your compute resources
   - Use auto-scaling
   - Consider spot instances (AWS) for non-critical workloads

## Backup Strategy

1. **Database Backups**
   - Supabase provides automatic backups
   - Export data regularly for additional safety

2. **Document Backups**
   - Keep original documents backed up
   - Version control for code

3. **Configuration Backups**
   - Store `.env.example` in git
   - Keep encrypted backups of actual `.env`

## Maintenance

### Regular Tasks
- Update dependencies monthly
- Monitor API usage and costs
- Review logs for errors
- Check API performance metrics
- Test disaster recovery procedures

### Emergency Procedures
- Document rollback procedures
- Keep previous version deployments available
- Have monitoring alerts configured
- Maintain incident response plan

## Support Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Uvicorn Documentation](https://www.uvicorn.org/)
