# 🌐 Nginx Configuration Guide

**Reverse Proxy Setup for Design Analysis System**

This guide explains the Nginx configuration that serves both the FastAPI backend and Streamlit frontend of your Design Analysis system.

## 🎯 Overview

The Nginx configuration acts as a reverse proxy that:
- **Routes API requests** (`/api/*`) to the FastAPI backend (port 8000)
- **Routes frontend requests** (`/`) to the Streamlit frontend (port 8501)
- **Provides security headers** and rate limiting
- **Handles SSL termination** (when configured)

## 📁 File Structure

```
deployment/
├── nginx/
│   └── nginx.conf          # Main Nginx configuration
├── systemd/
│   ├── design-analysis-api.service    # FastAPI service
│   └── streamlit-frontend.service     # Streamlit service
└── deploy_to_ec2.sh        # Deployment script
```

## 🔧 Configuration Details

### **Upstream Servers**

```nginx
upstream api_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

upstream streamlit_frontend {
    server 127.0.0.1:8501;
    keepalive 32;
}
```

### **API Routes (`/api/*`)**

```nginx
location /api/ {
    # Rate limiting
    limit_req zone=api burst=20 nodelay;
    
    # Proxy settings
    proxy_pass http://api_backend/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
    
    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}
```

### **Frontend Routes (`/`)**

```nginx
location / {
    # Rate limiting
    limit_req zone=streamlit burst=50 nodelay;
    
    # Proxy settings
    proxy_pass http://streamlit_frontend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
    
    # Timeouts (longer for Streamlit)
    proxy_connect_timeout 120s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;
    
    # WebSocket support for Streamlit
    proxy_set_header Connection "upgrade";
    proxy_set_header Upgrade $http_upgrade;
}
```

## 🚀 Deployment Steps

### **Step 1: Install Nginx**

```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y nginx

# On CentOS/RHEL
sudo yum install -y nginx
```

### **Step 2: Copy Configuration**

```bash
# Copy the Nginx configuration
sudo cp deployment/nginx/nginx.conf /etc/nginx/nginx.conf

# Test the configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
```

### **Step 3: Set Up Systemd Services**

```bash
# Copy service files
sudo cp deployment/systemd/design-analysis-api.service /etc/systemd/system/
sudo cp deployment/systemd/streamlit-frontend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable design-analysis-api
sudo systemctl enable streamlit-frontend

# Start services
sudo systemctl start design-analysis-api
sudo systemctl start streamlit-frontend
```

### **Step 4: Configure Firewall**

```bash
# Allow HTTP and HTTPS traffic
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# If using UFW
sudo ufw enable
```

## 🔒 Security Features

### **Rate Limiting**

```nginx
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=streamlit:10m rate=30r/s;

# Applied in location blocks
limit_req zone=api burst=20 nodelay;      # API routes
limit_req zone=streamlit burst=50 nodelay; # Frontend routes
```

### **Security Headers**

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

### **File Upload Limits**

```nginx
client_max_body_size 100M;  # Allow large file uploads
```

## 🔧 SSL/HTTPS Configuration

### **Using Let's Encrypt (Recommended)**

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **Manual SSL Configuration**

Uncomment and configure the HTTPS server block in `nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Same location blocks as HTTP
    location /api/ {
        proxy_pass http://api_backend/;
        # ... same proxy settings
    }
    
    location / {
        proxy_pass http://streamlit_frontend;
        # ... same proxy settings
    }
}
```

## 📊 Monitoring and Logging

### **Access Logs**

```bash
# View access logs
sudo tail -f /var/log/nginx/access.log

# View error logs
sudo tail -f /var/log/nginx/error.log

# Analyze traffic
sudo apt-get install -y goaccess
goaccess /var/log/nginx/access.log --log-format=COMBINED
```

### **Service Monitoring**

```bash
# Check service status
sudo systemctl status nginx
sudo systemctl status design-analysis-api
sudo systemctl status streamlit-frontend

# View service logs
sudo journalctl -u nginx -f
sudo journalctl -u design-analysis-api -f
sudo journalctl -u streamlit-frontend -f
```

## 🔍 Troubleshooting

### **Common Issues**

#### **502 Bad Gateway**
```bash
# Check if services are running
sudo systemctl status design-analysis-api
sudo systemctl status streamlit-frontend

# Check if ports are listening
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :8501

# Check service logs
sudo journalctl -u design-analysis-api -n 50
sudo journalctl -u streamlit-frontend -n 50
```

#### **504 Gateway Timeout**
```bash
# Increase timeouts in nginx.conf
proxy_connect_timeout 120s;
proxy_send_timeout 120s;
proxy_read_timeout 120s;
```

#### **413 Request Entity Too Large**
```bash
# Increase client_max_body_size in nginx.conf
client_max_body_size 100M;
```

### **Debugging Commands**

```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx

# Test upstream connectivity
curl -v http://localhost:8000/health
curl -v http://localhost:8501

# Check firewall rules
sudo ufw status
sudo iptables -L

# Monitor real-time traffic
sudo tcpdump -i any port 80 or port 443
```

## 🎨 Customization

### **Custom Error Pages**

```nginx
# Create custom error pages
location = /404.html {
    root /var/www/html;
    internal;
}

location = /50x.html {
    root /var/www/html;
    internal;
}
```

### **Caching Configuration**

```nginx
# Cache static files
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}

# Cache API responses (be careful with this)
location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_valid 404 1m;
    # ... other proxy settings
}
```

### **Load Balancing**

```nginx
# Multiple backend servers
upstream api_backend {
    server 127.0.0.1:8000 weight=3;
    server 127.0.0.1:8001 weight=1;
    keepalive 32;
}
```

## 📈 Performance Optimization

### **Gzip Compression**

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_proxied any;
gzip_comp_level 6;
gzip_types
    text/plain
    text/css
    text/xml
    text/javascript
    application/json
    application/javascript
    application/xml+rss
    application/atom+xml
    image/svg+xml;
```

### **Buffer Optimization**

```nginx
# API buffers
proxy_buffering on;
proxy_buffer_size 4k;
proxy_buffers 8 4k;
proxy_busy_buffers_size 8k;

# Frontend buffers (larger for Streamlit)
proxy_buffering on;
proxy_buffer_size 8k;
proxy_buffers 16 8k;
proxy_busy_buffers_size 16k;
```

## 🔄 Maintenance

### **Regular Tasks**

```bash
# Update Nginx
sudo apt-get update && sudo apt-get upgrade nginx

# Rotate logs
sudo logrotate /etc/logrotate.d/nginx

# Check SSL certificates
sudo certbot certificates

# Monitor disk space
df -h /var/log/nginx/

# Check for security updates
sudo apt-get update && sudo apt-get upgrade
```

### **Backup Configuration**

```bash
# Backup current configuration
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# Restore from backup
sudo cp /etc/nginx/nginx.conf.backup /etc/nginx/nginx.conf
sudo nginx -t && sudo systemctl reload nginx
```

## 🚀 Production Checklist

- [ ] **SSL Certificate** configured
- [ ] **Security Headers** enabled
- [ ] **Rate Limiting** configured
- [ ] **Logging** set up
- [ ] **Monitoring** configured
- [ ] **Backup** strategy in place
- [ ] **Firewall** rules configured
- [ ] **Error Pages** customized
- [ ] **Performance** optimized
- [ ] **Documentation** updated

The Nginx configuration provides a robust, secure, and performant reverse proxy for your Design Analysis system! 🎉
