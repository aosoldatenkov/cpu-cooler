#!/bin/bash
# Installation script for CPU Temperature Monitor Service

set -e

echo "Installing CPU Temperature Monitor Service..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)" 
   exit 1
fi

# Install required Python packages if not already installed
echo "Installing required Python packages..."
pip3 install psutil hidapi

# Copy the Python script to /usr/local/bin
echo "Installing CPU temperature monitor script..."
cp cpu_temp_monitor.py /usr/local/bin/
chmod +x /usr/local/bin/cpu_temp_monitor.py

# Copy the systemd service file
echo "Installing systemd service..."
cp cpu-temp-monitor.service /etc/systemd/system/

# Create log directory
mkdir -p /var/log
touch /var/log/cpu-temp-monitor.log

# Set up udev rules for USB device access (optional, for non-root execution)
echo "Setting up udev rules..."
cat > /etc/udev/rules.d/99-cpu-temp-monitor.rules << EOF
# Allow access to CPU temperature monitor USB device
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="aa88", ATTRS{idProduct}=="8666", MODE="0666", GROUP="users"
EOF

# Reload udev rules
udevadm control --reload-rules
udevadm trigger

# Reload systemd and enable the service
echo "Enabling and starting service..."
systemctl daemon-reload
systemctl enable cpu-temp-monitor.service
systemctl start cpu-temp-monitor.service

echo "Installation complete!"
echo ""
echo "Service status:"
systemctl status cpu-temp-monitor.service --no-pager
echo ""
echo "To view logs: journalctl -u cpu-temp-monitor.service -f"
echo "To stop service: systemctl stop cpu-temp-monitor.service"
echo "To disable service: systemctl disable cpu-temp-monitor.service"
