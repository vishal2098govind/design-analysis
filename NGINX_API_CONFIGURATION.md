# Nginx API Configuration Guide

## Overview

When running the Design Analysis System behind Nginx, the Streamlit frontend needs to be configured to make API requests through the Nginx proxy rather than directly to the FastAPI backend.

## Configuration Options

### Option 1: Relative URLs (Recommended for Production)

Set `API_BASE_URL` to an empty string in your `.env` file:

```bash
# .env file
API_BASE_URL=
```

This will make the Streamlit frontend use relative URLs like `/api/analyze` instead of absolute URLs like `http://localhost:8000/api/analyze`.

### Option 2: Explicit Domain (Alternative)

Set `API_BASE_URL` to your domain:

```bash
# .env file
API_BASE_URL=http://your-domain.com
```

## Nginx Configuration

The Nginx configuration in `deployment/nginx/aas.conf` already includes:

1. **CORS Headers**: Added to allow browser requests from the frontend
2. **API Proxy**: Routes `/api/*` requests to the FastAPI backend
3. **Preflight Handling**: Handles OPTIONS requests for CORS

## Testing the Configuration

### 1. Check API Health

```bash
# Test API directly
curl http://localhost:8000/health

# Test through Nginx
curl http://your-domain.com/api/health
```

### 2. Test Frontend API Connection

1. Open the Streamlit frontend
2. Go to Settings page
3. Check "API Configuration" section
4. Verify the connection test passes

### 3. Test Analysis Submission

1. Upload research data
2. Click "Start Analysis"
3. Check browser network tab for API requests
4. Verify requests go to `/api/analyze` (not localhost:8000)

## Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:

1. **Check Nginx CORS headers**: Ensure the Nginx configuration includes CORS headers
2. **Check FastAPI CORS**: Verify FastAPI has CORS middleware enabled
3. **Check API_BASE_URL**: Ensure it's configured correctly

### API Connection Failures

If the frontend can't connect to the API:

1. **Check Nginx logs**: `sudo tail -f /var/log/nginx/error.log`
2. **Check FastAPI logs**: `sudo journalctl -u design-analysis-api -f`
3. **Test direct connection**: Try accessing the API directly
4. **Check firewall**: Ensure port 80 is open

### Relative URL Issues

If relative URLs don't work:

1. **Check Nginx location block**: Ensure `/api/` routes to FastAPI
2. **Check proxy_pass**: Should be `http://127.0.0.1:8000`
3. **Check headers**: Ensure proper headers are forwarded

## Example Configuration

### Development (.env)
```bash
API_BASE_URL=http://localhost:8000
```

### Production (.env)
```bash
API_BASE_URL=
```

### Nginx (aas.conf)
```nginx
location /api/ {
    # CORS headers
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
    
    # Handle preflight
    if ($request_method = 'OPTIONS') {
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization';
        add_header 'Access-Control-Max-Age' 1728000;
        add_header 'Content-Type' 'text/plain; charset=utf-8';
        add_header 'Content-Length' 0;
        return 204;
    }
    
    # Proxy to FastAPI
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## Security Considerations

1. **CORS Origin**: In production, consider restricting CORS origins to your specific domain
2. **HTTPS**: Use HTTPS in production for secure communication
3. **Rate Limiting**: Consider adding rate limiting to prevent abuse
4. **Authentication**: Add authentication if needed for production use

## Monitoring

Monitor the following logs for issues:

```bash
# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# FastAPI logs
sudo journalctl -u design-analysis-api -f

# Streamlit logs
sudo journalctl -u aas-frontend -f
```
