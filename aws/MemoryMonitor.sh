#!/bin/bash

# Switch to root user
sudo su

# Update and upgrade the system
apt update && apt -y upgrade

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
