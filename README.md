configuration of digitalocean

1. Create Ubuntu Droplet on DigitalOcean
DigitalOcean Dashboard:
Choose Ubuntu 22.04 LTS
Select droplet size (Basic $6/month is good to start)
Choose datacenter region (Singapore for Malaysia)
Add SSH key (or use password)
Create droplet


2. Initial Server Setup
bash
# SSH into your server
ssh root@your_server_ip

# Update system packages
apt update
apt upgrade -y

# Create an admin user for server management (not for running the app)
adduser deploy
usermod -aG sudo deploy

# Add deploy user to www-data group
usermod -aG www-data deploy

# Set up firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable

# Switch to your admin user
su - deploy

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install additional system dependencies
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y

# Install Nginx
sudo apt install nginx -y

# Install Git
sudo apt install git -y

# Verify installations
python3 --version
pip3 --version
nginx -v

# Create virtual environment as www-data user
sudo -u www-data python3 -m venv /var/www/mystreamlit/venv

# Activate virtual environment
source /var/www/mystreamlit/venv/bin/activate

# Install dependencies
sudo -u www-data /var/www/mystreamlit/venv/bin/pip install --upgrade pip
sudo -u www-data /var/www/mystreamlit/venv/bin/pip install -r /var/www/mystreamlit/requirement.txt

# Install additional packages if needed
sudo -u www-data /var/www/mystreamlit/venv/bin/pip install streamlit pandas python-dotenv

# Create .env file
sudo nano /var/www/mystreamlit/.env

# Create Streamlit directories with proper permissions
sudo mkdir -p /var/www/.streamlit
sudo chown -R www-data:www-data /var/www/.streamlit
sudo chmod -R 755 /var/www/.streamlit

sudo mkdir -p /var/www/mystreamlit/.streamlit
sudo chown -R www-data:www-data /var/www/mystreamlit/.streamlit
sudo chmod -R 755 /var/www/mystreamlit/.streamlit

# Test Streamlit app
cd /var/www/mystreamlit
sudo -u www-data bash -c 'export HOME=/var/www/mystreamlit && export OPENROUTER_API_KEY="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" && export OPENROUTER_MODEL_ID="google/gemini-2.0-flash-001" && /var/www/mystreamlit/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0'

# Open firewall for testing
sudo ufw allow 8501

# Test from browser: http://159.223.48.224:8501
# Press Ctrl+C to stop the test server

# Create systemd service file
sudo nano /etc/systemd/system/mystreamlit.service

[Unit]
Description=Streamlit instance to serve mystreamlit
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/mystreamlit
Environment="PATH=/var/www/mystreamlit/venv/bin"
Environment="HOME=/var/www/mystreamlit"
Environment="OPENROUTER_API_KEY=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"
Environment="OPENROUTER_MODEL_ID=google/gemini-2.0-flash-001"
ExecStart=/var/www/mystreamlit/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Reload systemd to read new service
sudo systemctl daemon-reload

# Start the service
sudo systemctl start mystreamlit

# Enable service to start on boot
sudo systemctl enable mystreamlit

# Check status
sudo systemctl status mystreamlit

# View logs if needed
sudo journalctl -u mystreamlit -f

# Create Nginx configuration file
sudo nano /etc/nginx/sites-available/mystreamlit

server {
    listen 80;
    server_name 159.223.48.224;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Max upload size
    client_max_body_size 100M;

    # Access and error logs
    access_log /var/log/nginx/mystreamlit_access.log;
    error_log /var/log/nginx/mystreamlit_error.log;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# Create symbolic link
sudo ln -s /etc/nginx/sites-available/mystreamlit /etc/nginx/sites-enabled/

# Remove default Nginx site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Check Nginx status
sudo systemctl status nginx

# Restart your Streamlit app
sudo systemctl restart mystreamlit

# View Streamlit app logs
sudo journalctl -u mystreamlit -f

# Stop Streamlit app
sudo systemctl stop mystreamlit

# Start Streamlit app
sudo systemctl start mystreamlit

# Restart Nginx
sudo systemctl restart nginx

# View Nginx error logs
sudo tail -f /var/log/nginx/mystreamlit_error.log

# View Nginx access logs
sudo tail -f /var/log/nginx/mystreamlit_access.log

# Check server IP
curl ifconfig.me

# Check firewall status
sudo ufw status

# Check if Streamlit service is running
sudo systemctl status mystreamlit

# Check Nginx status
sudo systemctl status nginx

# View all files in app directory
ls -la /var/www/mystreamlit/

# Check .env file
sudo cat /var/www/mystreamlit/.env

# Check file permissions
ls -la /var/www/mystreamlit/

# Fix ownership (if needed)
sudo chown -R www-data:www-data /var/www/mystreamlit

# Fix permissions (if needed)
sudo chmod -R 755 /var/www/mystreamlit


