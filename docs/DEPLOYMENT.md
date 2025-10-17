# Deployment Guide

## Production Deployment Checklist

### Pre-Deployment

- [ ] Review all environment variables
- [ ] Generate secure API keys
- [ ] Configure MongoDB with authentication
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy
- [ ] Review rate limits
- [ ] Test error handling
- [ ] Document runbook

### Deployment Steps

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Application Setup

```bash
# Clone repository
git clone https://github.com/yourusername/books-crawler.git
cd books-crawler

# Create production environment file
cp .env.example .env.production

# Edit with production settings
nano .env.production
```

#### 3. MongoDB Setup

**Option A: Local MongoDB**

```bash
# Create data directory
mkdir -p /data/mongodb

# Run MongoDB with authentication
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v /data/mongodb:/data/db \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secure_password \
  mongo:7.0
```

**Option B: MongoDB Atlas** (Recommended for production)

1. Create cluster at https://cloud.mongodb.com
2. Configure network access
3. Create database user
4. Get connection string
5. Update MONGODB_URL in .env

#### 4. Deploy with Docker Compose

```bash
# Pull latest images
docker-compose pull

# Start services
docker-compose -f docker-compose.yml --env-file .env.production up -d

# Check logs
docker-compose logs -f
```

#### 5. Configure Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 6. Set Up SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Monitoring

#### Health Checks

```bash
# API health
curl https://api.yourdomain.com/health

# Database health
docker exec mongodb mongosh --eval "db.adminCommand('ping')"
```

#### Log Monitoring

```bash
# View application logs
docker-compose logs -f crawler-api

# View MongoDB logs
docker-compose logs -f mongodb

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

#### Resource Monitoring

```bash
# Container stats
docker stats

# Disk usage
df -h

# Memory usage
free -h
```

### Backup Strategy

#### Database Backup

```bash
# Manual backup
docker exec mongodb mongodump \
  --out=/backup/$(date +%Y%m%d) \
  --db=books_crawler

# Automated daily backup (cron)
0 2 * * * /path/to/backup-script.sh
```

**backup-script.sh:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/mongodb/$DATE"

# Create backup
docker exec mongodb mongodump \
  --out=/backup/$DATE \
  --db=books_crawler

# Compress
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Keep only last 7 days
find /backups/mongodb -name "*.tar.gz" -mtime +7 -delete
```

### Scaling

#### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  crawler-api:
    deploy:
      replicas: 3
    depends_on:
      - mongodb
      - nginx-lb

  nginx-lb:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
```

#### Vertical Scaling

Adjust resource limits in docker-compose.yml:

```yaml
services:
  crawler-api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Security Hardening

1. **Environment Variables**
   - Use Docker secrets or encrypted vaults
   - Never commit .env files

2. **API Keys**
   - Rotate regularly (monthly)
   - Use strong, random keys (32+ chars)

3. **MongoDB**
   - Enable authentication
   - Use strong passwords
   - Limit network access

4. **Container Security**
   - Run as non-root user
   - Scan images for vulnerabilities
   - Keep images updated

5. **Network**
   - Use private networks
   - Configure firewall rules
   - Enable rate limiting

### Troubleshooting

#### Common Issues

**API not responding:**
```bash
# Check container status
docker ps

# Check logs
docker-compose logs crawler-api

# Restart service
docker-compose restart crawler-api
```

**Database connection errors:**
```bash
# Check MongoDB status
docker exec mongodb mongosh --eval "db.adminCommand('ping')"

# Check connection string in .env
cat .env.production | grep MONGODB_URL

# Restart MongoDB
docker-compose restart mongodb
```

**High memory usage:**
```bash
# Check stats
docker stats

# Reduce concurrent requests
# Edit .env: CRAWLER_MAX_CONCURRENT_REQUESTS=5

# Restart
docker-compose restart crawler-api
```

### Rollback Procedure

```bash
# Stop current version
docker-compose down

# Checkout previous version
git checkout <previous-commit>

# Restore database backup if needed
docker exec mongodb mongorestore --db books_crawler /backup/<date>

# Start previous version
docker-compose up -d

# Verify
curl https://api.yourdomain.com/health
```

### Maintenance Windows

Recommended schedule:
- **Weekly**: Review logs and metrics
- **Monthly**: Update dependencies and rotate keys
- **Quarterly**: Full security audit
- **Yearly**: Infrastructure review

### Support

For production issues:
1. Check logs first
2. Review monitoring dashboards
3. Consult troubleshooting guide
4. Contact development team
5. Escalate if critical
