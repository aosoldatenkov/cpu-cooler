# CPU Cooler display on Linux

This script shows CPU temperature on the display of a water cooler.

Tested with the Rise Mode water cooler

![](images/cpu-cooler.jpg)

## CPU temperature

The service will automatically start on boot and restart if it crashes. The script handles different CPU temperature sensors.
It is configuted to use the tctl temperature from k10temp linux module as the primary option. More details [here](https://www.kernel.org/doc/html/v5.6/hwmon/k10temp.html#:~:text=Tctl%20is%20the%20processor%20temperature,like%20die%20or%20case%20temperature.).

## Installation

# First identify the vendor id and product id of your device. You can use the `lsusb` utility. Then replace the `VENDOR_ID` and `PRODUCT_ID` in the cpu_temp_monitor.py script.

# Save the three files cpu_temp_monitor.py, cpu-temp-monitor.service and install.sh
in the same directory.

# Make the install script executable:

chmod +x install.sh

# Run the installation script:

sudo ./install.sh

## Manual Installation (alternative)

If you prefer to install manually:

# Install dependencies
sudo pip3 install psutil hidapi

# Copy files
sudo cp cpu_temp_monitor.py /usr/local/bin/
sudo chmod +x /usr/local/bin/cpu_temp_monitor.py
sudo cp cpu-temp-monitor.service /etc/systemd/system/

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable cpu-temp-monitor.service
sudo systemctl start cpu-temp-monitor.service

## Useful Commands:

# Check service status: systemctl status cpu-temp-monitor.service
# View logs: journalctl -u cpu-temp-monitor.service -f
# Stop service: systemctl stop cpu-temp-monitor.service
# Restart service: systemctl restart cpu-temp-monitor.service
