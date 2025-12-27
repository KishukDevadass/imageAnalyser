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
