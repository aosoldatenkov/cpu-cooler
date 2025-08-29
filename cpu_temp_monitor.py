#!/usr/bin/env python3
"""
CPU Temperature Monitor Service
Monitors CPU temperature and sends it to a USB HID device display
"""

import hid
import psutil
import time
import signal
import sys
import logging
from pathlib import Path

# Configuration
VENDOR_ID = 0xaa88
PRODUCT_ID = 0x8666
UPDATE_INTERVAL = 1  # seconds
LOG_FILE = '/var/log/cpu-temp-monitor.log'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CPUTempMonitor:
    def __init__(self):
        self.device = None
        self.running = False
        
    def get_cpu_temp(self):
        """Get CPU temperature from sensors"""
        try:
            temps = psutil.sensors_temperatures()
            if 'k10temp' in temps:
                return temps['k10temp'][0].current
            elif 'coretemp' in temps:
                return temps['coretemp'][0].current
            else:
                # Fallback: try to get any CPU temperature
                for sensor_name, sensor_list in temps.items():
                    if 'cpu' in sensor_name.lower() or 'core' in sensor_name.lower():
                        return sensor_list[0].current
                logger.warning("No CPU temperature sensor found")
                return 0
        except Exception as e:
            logger.error(f"Error reading CPU temperature: {e}")
            return 0
    
    def connect_device(self):
        """Connect to the USB HID device"""
        try:
            self.device = hid.device()
            self.device.open(VENDOR_ID, PRODUCT_ID)
            logger.info(f"Connected to USB device (VID: {hex(VENDOR_ID)}, PID: {hex(PRODUCT_ID)})")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to USB device: {e}")
            return False
    
    def write_temperature(self, temperature):
        """Write temperature to the USB device"""
        if not self.device:
            return False
            
        try:
            # Ensure temperature is within display range
            display_temp = max(0, min(255, int(temperature)))
            byte_commands = [display_temp]
            num_bytes_written = self.device.write(byte_commands)
            logger.debug(f"Wrote temperature {temperature}°C to device ({num_bytes_written} bytes)")
            return True
        except IOError as e:
            logger.error(f"Error writing to device: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.device:
            try:
                self.device.close()
                logger.info("Device connection closed")
            except Exception as e:
                logger.error(f"Error closing device: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def run(self):
        """Main service loop"""
        logger.info("Starting CPU Temperature Monitor Service")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Connect to device
        if not self.connect_device():
            logger.error("Failed to connect to device, exiting")
            sys.exit(1)
        
        self.running = True
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        try:
            while self.running:
                try:
                    # Get CPU temperature
                    cpu_temp = self.get_cpu_temp()
                    
                    # Write to device
                    if self.write_temperature(cpu_temp):
                        consecutive_errors = 0
                        logger.debug(f"CPU Temperature: {cpu_temp}°C")
                    else:
                        consecutive_errors += 1
                        logger.warning(f"Failed to write temperature (error {consecutive_errors}/{max_consecutive_errors})")
                        
                        if consecutive_errors >= max_consecutive_errors:
                            logger.error("Too many consecutive errors, attempting to reconnect...")
                            self.cleanup()
                            if not self.connect_device():
                                logger.error("Reconnection failed, exiting")
                                break
                            consecutive_errors = 0
                    
                    time.sleep(UPDATE_INTERVAL)
                    
                except KeyboardInterrupt:
                    logger.info("Received keyboard interrupt")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error in main loop: {e}")
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error("Too many errors, exiting")
                        break
                    time.sleep(UPDATE_INTERVAL)
        
        finally:
            self.cleanup()
            logger.info("CPU Temperature Monitor Service stopped")

def main():
    """Entry point"""
    monitor = CPUTempMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
