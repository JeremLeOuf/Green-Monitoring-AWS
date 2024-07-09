#!/bin/bash

# Switch to root user
sudo su

# Update and upgrade the system
apt update && apt -y upgrade

# Install stress-ng and iperf
apt -y install stress-ng iperf

# Reboot the system
sudo reboot

# After reboot, continue with script execution
sleep 60  # Wait for 1 minute after reboot (adjust as needed)

# Script continues after reboot

######## LAMP INSTALLATION ########

# PASSWORD IS " bGGik5cq4mmuTKti69^ "

###################################

# Install stress-ng, iperf, Apache, MySQL, PHP, and other packages
sudo apt -y install stress-ng iperf apache2 mysql-server php libapache2-mod-php

# Secure MySQL server installation with pre-configured passwords
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password bGGik5cq4mmuTKti69^'
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password bGGik5cq4mmuTKti69^'
sudo apt -y install mysql-server

# Secure Apache and set ServerName
echo "ServerName localhost" | sudo tee -a /etc/apache2/apache2.conf

# Enable the default website
sudo a2ensite 000-default.conf

# Restart Apache
sudo systemctl restart apache2

# Download and extract WordPress
wget -qO- https://wordpress.org/latest.tar.gz | sudo tar -xz -C /var/www/html/

# Set ownership and permissions
sudo chown -R www-data:www-data /var/www/html/
sudo chmod -R 755 /var/www/html/

# Inform about successful installation
echo "LAMP stack, stress-ng, iperf, and WordPress successfully installed!"

# Create the stress test script
cat <<'EOF' | sudo tee /home/ubuntu/hardware_stress.sh > /dev/null
#!/bin/bash

# Run CPU stress test on 2 cores for 1 hour
stress-ng --cpu 2 --timeout 3600s

EOF

# Make the stress test script executable
sudo chmod +x /home/ubuntu/hardware_stress.sh

# Start iperf network load test to server for 1 hour
timeout 3600 nohup iperf -c 16.171.200.246 &

# Inform about starting scripts
echo "Starting hardware and network load tests..."
