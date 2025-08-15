#!/bin/bash
# User data script for EC2 instance setup
# This script automatically configures the EC2 instance for the Design Analysis API

set -e  # Exit on any error

echo "🚀 Starting EC2 instance setup for Design Analysis API..."

# Update system
echo "📦 Updating system packages..."
yum update -y

# Install Python 3.11 and pip
echo "🐍 Installing Python 3.11..."
yum install -y python3.11 python3.11-pip python3.11-devel

# Install development tools
echo "🔧 Installing development tools..."
yum groupinstall -y "Development Tools"
yum install -y git nginx

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /opt/design-analysis
cd /opt/design-analysis

# Clone your repository (replace with your repo URL)
echo "📥 Cloning repository..."
git clone https://github.com/yourusername/design-analysis.git .

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
STORAGE_TYPE=s3
S3_BUCKET_NAME=design-analysis-production
S3_REGION=us-east-1
S3_PREFIX=design-analysis
EOF

# Create systemd service
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/design-analysis.service << EOF
[Unit]
Description=Design Analysis API
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/design-analysis
Environment=PATH=/opt/design-analysis/venv/bin
ExecStart=/opt/design-analysis/venv/bin/python api_s3.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "🚀 Starting Design Analysis service..."
systemctl enable design-analysis
systemctl start design-analysis

# Install and configure nginx
echo "🌐 Configuring nginx..."
cat > /etc/nginx/conf.d/design-analysis.conf << EOF
upstream design_analysis {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://design_analysis;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
EOF

# Start nginx
systemctl enable nginx
systemctl start nginx

# Configure firewall
echo "🔥 Configuring firewall..."
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload

# Create health check script
echo "🏥 Creating health check script..."
cat > /opt/design-analysis/health-check.sh << 'EOF'
#!/bin/bash
curl -f http://localhost:8000/health || exit 1
EOF

chmod +x /opt/design-analysis/health-check.sh

# Add health check to crontab
echo "*/5 * * * * /opt/design-analysis/health-check.sh" | crontab -

# Increase file descriptors
echo "📈 Optimizing system limits..."
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Create deployment log
echo "📝 Creating deployment log..."
cat > /opt/design-analysis/deployment.log << EOF
Deployment completed at: $(date)
Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)
Region: $(curl -s http://169.254.169.254/latest/meta-data/placement/region)
EOF

echo "✅ EC2 instance setup completed successfully!"
echo "🌐 API should be available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "📊 Health check: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/health"
