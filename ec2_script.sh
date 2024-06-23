#!/bin/bash

# Switch to root user
sudo su

# Update and upgrade the system
apt update && apt -y upgrade

# Install stress-ng and iperf
apt -y install stress-ng iperf


##### LAMP INSTALLATION #####

# PASSWORD IS "bGGik5cq4mmuTKti69"


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

# Install the Amazon CloudWatch Agent
wget https://amazoncloudwatch-agent.s3.amazonaws.com/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i -E ./amazon-cloudwatch-agent.deb

# Create the CloudWatch Agent configuration file
cat <<'EOF' > /home/ubuntu/cw_agent.json
{
  "metrics": {
    "namespace": "CWAgent",
    "metrics_collected": {
      "mem": {
        "measurement": [
          {"name": "mem_used_percent", "rename": "MemoryUtilization", "unit": "Percent"}
        ],
        "metrics_collection_interval": 60
      }
    }
  }
}
EOF

# Start the CloudWatch Agent with the configuration file
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/home/ubuntu/cw_agent.json -s

echo "CloudWatch agent configured and started."

# Create the stress test script
cat <<'EOF' > /home/ubuntu/ec2_hardware_stress.sh
#!/bin/bash

while true; do
    # Run CPU stress test for 10 minutes
    stress-ng --cpu 2 --timeout 600s
    
    # Run memory stress test for 10 minutes
    stress-ng --vm 1 --vm-bytes 512M --timeout 600s
    
    # Sleep for 5 minutes to let the instance recover
    sleep 300s
done
EOF

# Make the stress test script executable
chmod +x /home/ubuntu/ec2_hardware_stress.sh

echo "Starting the network load script..."

# Starts an iperf client in the background to my webserver server for 20mins
nohup iperf -c  &

echo "Starting the hardware load script..."

# Run the stress test script in the background
nohup /home/ubuntu/ec2_hardware_stress.sh &