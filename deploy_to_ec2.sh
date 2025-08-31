#!/bin/bash

# Design Analysis System Deployment Script
# Deploys both FastAPI backend and Streamlit frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
EC2_HOST=""
EC2_USER="ubuntu"
PROJECT_DIR="/home/ubuntu/design_analysis"
VENV_DIR="$PROJECT_DIR/venv"

echo -e "${BLUE}🚀 Design Analysis System Deployment${NC}"
echo "=================================="

# Check if host is provided
if [ -z "$EC2_HOST" ]; then
    echo -e "${YELLOW}Please set EC2_HOST environment variable or edit this script${NC}"
    echo "Usage: EC2_HOST=your-ec2-ip ./deploy_to_ec2.sh"
    exit 1
fi

echo -e "${GREEN}Deploying to: $EC2_HOST${NC}"

# Function to run commands on EC2
run_on_ec2() {
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$EC2_USER@$EC2_HOST" "$1"
}

# Function to copy files to EC2
copy_to_ec2() {
    scp -o StrictHostKeyChecking=no -o ConnectTimeout=10 -r "$1" "$EC2_USER@$EC2_HOST:$2"
}

echo -e "${BLUE}📋 Step 1: Checking EC2 connection...${NC}"
if ! run_on_ec2 "echo 'Connection successful'"; then
    echo -e "${RED}❌ Failed to connect to EC2 instance${NC}"
    exit 1
fi
echo -e "${GREEN}✅ EC2 connection successful${NC}"

echo -e "${BLUE}📋 Step 2: Creating project directory...${NC}"
run_on_ec2 "mkdir -p $PROJECT_DIR"
echo -e "${GREEN}✅ Project directory created${NC}"

echo -e "${BLUE}📋 Step 3: Copying project files...${NC}"
copy_to_ec2 "." "$PROJECT_DIR/"
echo -e "${GREEN}✅ Project files copied${NC}"

echo -e "${BLUE}📋 Step 4: Installing system dependencies...${NC}"
run_on_ec2 "sudo apt-get update && sudo apt-get install -y python3-pip python3-venv nginx"
echo -e "${GREEN}✅ System dependencies installed${NC}"

echo -e "${BLUE}📋 Step 5: Setting up Python virtual environment...${NC}"
run_on_ec2 "cd $PROJECT_DIR && python3 -m venv venv"
run_on_ec2 "cd $PROJECT_DIR && source venv/bin/activate && pip install --upgrade pip"
echo -e "${GREEN}✅ Virtual environment created${NC}"

echo -e "${BLUE}📋 Step 6: Installing Python dependencies...${NC}"
run_on_ec2 "cd $PROJECT_DIR && source venv/bin/activate && pip install -r requirements.txt"
echo -e "${GREEN}✅ Python dependencies installed${NC}"

echo -e "${BLUE}📋 Step 7: Setting up Nginx configuration...${NC}"
run_on_ec2 "sudo cp $PROJECT_DIR/deployment/nginx/nginx.conf /etc/nginx/nginx.conf"
run_on_ec2 "sudo nginx -t"
run_on_ec2 "sudo systemctl enable nginx"
run_on_ec2 "sudo systemctl restart nginx"
echo -e "${GREEN}✅ Nginx configured and started${NC}"

echo -e "${BLUE}📋 Step 8: Setting up systemd services...${NC}"

# API service
run_on_ec2 "sudo cp $PROJECT_DIR/deployment/systemd/design-analysis-api.service /etc/systemd/system/"
run_on_ec2 "sudo systemctl daemon-reload"
run_on_ec2 "sudo systemctl enable design-analysis-api"

# Streamlit frontend service
run_on_ec2 "sudo cp $PROJECT_DIR/deployment/systemd/streamlit-frontend.service /etc/systemd/system/"
run_on_ec2 "sudo systemctl daemon-reload"
run_on_ec2 "sudo systemctl enable streamlit-frontend"

echo -e "${GREEN}✅ Systemd services configured${NC}"

echo -e "${BLUE}📋 Step 9: Setting up environment variables...${NC}"
run_on_ec2 "cd $PROJECT_DIR && cp .env.example .env"
echo -e "${YELLOW}⚠️  Please edit the .env file on the EC2 instance with your actual values${NC}"
echo -e "${YELLOW}   Run: ssh $EC2_USER@$EC2_HOST 'nano $PROJECT_DIR/.env'${NC}"

echo -e "${BLUE}📋 Step 10: Starting services...${NC}"
run_on_ec2 "sudo systemctl start design-analysis-api"
run_on_ec2 "sudo systemctl start streamlit-frontend"
echo -e "${GREEN}✅ Services started${NC}"

echo -e "${BLUE}📋 Step 11: Checking service status...${NC}"
run_on_ec2 "sudo systemctl status design-analysis-api --no-pager -l"
run_on_ec2 "sudo systemctl status streamlit-frontend --no-pager -l"
run_on_ec2 "sudo systemctl status nginx --no-pager -l"

echo -e "${BLUE}📋 Step 12: Testing endpoints...${NC}"
echo -e "${YELLOW}Testing API health endpoint...${NC}"
run_on_ec2 "curl -s http://localhost:8000/health || echo 'API not responding'"

echo -e "${YELLOW}Testing frontend accessibility...${NC}"
run_on_ec2 "curl -s http://localhost:8501 | head -20 || echo 'Frontend not responding'"

echo -e "${YELLOW}Testing Nginx proxy...${NC}"
run_on_ec2 "curl -s http://localhost/health || echo 'Nginx not responding'"

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Service Information:${NC}"
echo -e "   API Backend: http://$EC2_HOST:8000"
echo -e "   Frontend: http://$EC2_HOST:8501"
echo -e "   Nginx Proxy: http://$EC2_HOST"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo -e "   Check API status: ssh $EC2_USER@$EC2_HOST 'sudo systemctl status design-analysis-api'"
echo -e "   Check Frontend status: ssh $EC2_USER@$EC2_HOST 'sudo systemctl status streamlit-frontend'"
echo -e "   Check Nginx status: ssh $EC2_USER@$EC2_HOST 'sudo systemctl status nginx'"
echo -e "   View API logs: ssh $EC2_USER@$EC2_HOST 'sudo journalctl -u design-analysis-api -f'"
echo -e "   View Frontend logs: ssh $EC2_USER@$EC2_HOST 'sudo journalctl -u streamlit-frontend -f'"
echo -e "   View Nginx logs: ssh $EC2_USER@$EC2_HOST 'sudo tail -f /var/log/nginx/access.log'"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo -e "   1. Edit the .env file with your actual configuration values"
echo -e "   2. Configure your security groups to allow HTTP/HTTPS traffic"
echo -e "   3. Set up SSL certificates for production use"
echo -e "   4. Configure your domain name to point to the EC2 instance"
echo ""
echo -e "${GREEN}🚀 Your Design Analysis System is now running!${NC}"
