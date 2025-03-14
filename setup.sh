#!/bin/bash

# Update system
sudo apt update
sudo apt upgrade -y

# Install dependencies
sudo apt install -y nginx

# Deploy your application
sudo cp -r /path/to/deploy /var/www/html

# Restart services
sudo systemctl restart nginx