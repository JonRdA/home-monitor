import logging
from typing import Dict, Optional

import psutil

from .abstract_sensor import Sensor

logger = logging.getLogger(__name__)

class SystemMonitorSensor(Sensor):
    """
    A virtual sensor that reads system metrics from the device it's running on.
    """
    def __init__(self, config: dict):
        super().__init__(config)
        # Initialize network counters at startup to measure differences later
        self._last_net_io = psutil.net_io_counters()
        logger.info("SystemMonitorSensor initialized.")

    def _get_cpu_temperature(self) -> Optional[float]:
        """Reads the CPU temperature from the system file on a Raspberry Pi."""
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = int(f.read().strip()) / 1000.0
            return round(temp, 2)
        except FileNotFoundError:
            # This will happen if not on a Pi, which is fine for dev
            logger.debug("CPU temp file not found. Not running on a Pi?")
            return None
        except Exception:
            logger.warning("Could not read CPU temperature.", exc_info=True)
            return None

    def _get_fan_status(self) -> int:
        """
        Placeholder for reading fan status.
        This is hardware-specific. You might check a GPIO pin.
        Returns 1 for ON, 0 for OFF.
        """
        # Example: check a specific GPIO pin if you have a fan controller
        # import RPi.GPIO as GPIO
        # FAN_GPIO = 18
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(FAN_GPIO, GPIO.IN)
        # return GPIO.input(FAN_GPIO)
        return 0 # Defaulting to OFF for now

    def read(self) -> Optional[Dict[str, float]]:
        """Reads a variety of system metrics."""
        logger.debug(f"Reading from {self.id}...")
        
        # --- Network Usage ---
        current_net_io = psutil.net_io_counters()
        bytes_sent = current_net_io.bytes_sent - self._last_net_io.bytes_sent
        bytes_recv = current_net_io.bytes_recv - self._last_net_io.bytes_recv
        self._last_net_io = current_net_io # Update baseline for next reading

        # --- Other Metrics ---
        cpu_usage = psutil.cpu_percent(interval=None) # Non-blocking
        memory_usage = psutil.virtual_memory().percent
        cpu_temp = self._get_cpu_temperature()
        fan_on = self._get_fan_status()
        
        data = {
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": memory_usage,
            "network_bytes_sent": bytes_sent,
            "network_bytes_recv": bytes_recv,
            "fan_on": float(fan_on), # InfluxDB likes floats or ints
        }
        
        if cpu_temp is not None:
            data["cpu_temperature"] = cpu_temp

        return data