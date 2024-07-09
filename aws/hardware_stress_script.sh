#!/bin/bash

# Switch to root user
sudo su

# Update and upgrade the system
apt update && apt -y upgrade

# Install stress-ng and iperf
apt -y install stress-ng iperf

######## LAMP INSTALLATION ########

# PASSWORD IS " bGGik5cq4mmuTKti69^ "

###################################

# Install Apache web server
apt -y install apache2

# Secure Apache
echo "ServerName localhost" >> /etc/apache2/sites-available/000-default.conf

# Enable the website
a2ensite 000-default.conf

# Restart Apache
systemctl restart apache2

# Install MySQL server with pre-configured strong password
echo "mysql-server mysql-server/root password password bGGik5cq4mmuTKti69^ | debconf-set-selections
echo "mysql-server mysql-server/re-root password bGGik5cq4mmuTKti69^| debconf-set-selections
apt -y install mysql-server

# Install PHP
apt -y install php libapache2-mod-php

# Create a database for WordPress
echo "CREATE DATABASE wordpress CHARACTER SET utf8 COLLATE utf8_general_ci;" | mysql -u root -p "bGGik5cq4mmuTKti69^"

# Download latest WordPress
wget https://wordpress.org/latest.tar.gz

# Extract WordPress files
tar -xzf latest.tar.gz

# Move WordPress files to document root
mv wordpress/* /var/www/html/

# Download WordPress security keys
KEYS=$(curl -s https://api.wordpress.org/secret-key/1.1/salt/)

# Extract individual keys (modify variable names if needed)
AUTH_KEY=$(echo "$KEYS" | grep AUTH_KEY | cut -d "'" -f2)
SECURE_AUTH_KEY=$(echo "$KEYS" | grep SECURE_AUTH_KEY | cut -d "'" -f2)
LOGGED_IN_KEY=$(echo "$KEYS" | grep LOGGED_IN_KEY | cut -d "'" -f2)
NONCE_KEY=$(echo "$KEYS" | grep NONCE_KEY | cut -d "'" -f2)
AUTH_SALT=$(echo "$KEYS" | grep AUTH_SALT | cut -d "'" -f2)
SECURE_AUTH_SALT=$(echo "$KEYS" | grep AUTH_SALT | cut -d "'" -f2)
LOGGED_IN_SALT=$(echo "$KEYS" | grep AUTH_SALT | cut -d "'" -f2)
NONCE_SALT=$(echo "$KEYS" | grep AUTH_SALT | cut -d "'" -f2)

# Set ownership and permissions for security
chown -R www-data:www-data /var/www/html/
chmod -R 755 /var/www/html/

# Restart Apache
systemctl restart apache2

echo "LAMP stack, stress-ng, iperf, and WordPress successfully installed!"

# Create the stress test script
cat <<'EOF' > /home/ubuntu/hardware_stress.sh
#!/bin/bash

# Run CPU stress test on 2 cores for 1 hour
stress-ng --cpu 2 --timeout 3600s

done
EOF

# Make the stress test script executable
chmod +x /home/ubuntu/hardware_stress.sh

echo "Starting the network load script..."

# Starts an iperf client in the background to my webserver server for 1hr
timeout 3600 nohup iperf -c 16.171.200.246 &

echo "Starting the hardware load script..."

# Run the stress test script in the background
nohup /home/ubuntu/hardware_stress.sh &
