# src/main.py
import json
import logging
import time
from datetime import datetime
from typing import List

import paho.mqtt.client as mqtt
from config import CONFIG, MQTT_BROKER_HOST
from logging_config import setup_logging
from sensors.abstract_sensor import Sensor
from sensors.aht20_bmp280 import AHT20_BMP280_Sensor
from sensors.mock import MockSensor
from sensors.system import SystemMonitorSensor

# --- Setup ---
setup_logging()
logger = logging.getLogger(__name__)

# --- Helper Functions ---
def get_sensor(sensor_config: dict) -> Sensor:
    """Factory function to get a sensor instance based on config."""
    sensor_type = sensor_config.get("type")
    if sensor_type == "aht20_bmp280":
        return AHT20_BMP280_Sensor(sensor_config)
    if sensor_type == "mock":
        return MockSensor(sensor_config)
    if sensor_type == "system": # <-- ADD THIS
        return SystemMonitorSensor(sensor_config)
    
    raise ValueError(f"Unknown sensor type: {sensor_type}")


def load_sensors(config: dict) -> List[Sensor]:
    """Loads all enabled sensor instances from the configuration."""
    sensors = []
    for sensor_conf in config.get("sensors", []):
        if sensor_conf.get("enabled", False):
            try:
                sensor = get_sensor(sensor_conf)
                sensors.append(sensor)
                logger.info(f"Successfully loaded sensor: {sensor_conf.get('id')}")
            except (ValueError, KeyError) as e:
                logger.error(f"Failed to load sensor '{sensor_conf.get('id')}': {e}")
    return sensors


def connect_mqtt(client_id: str) -> mqtt.Client:
    """Connects to the MQTT broker and starts the network loop."""
    client = mqtt.Client(client_id=client_id)
    try:
        client.connect(MQTT_BROKER_HOST)
        client.loop_start()
        logger.info(f"Connected to MQTT Broker at {MQTT_BROKER_HOST}")
        return client
    except Exception:
        logger.error(f"Could not connect to MQTT Broker at {MQTT_BROKER_HOST}", exc_info=True)
        # In a real scenario, you might want to retry here before exiting
        exit(1)


def publish_reading(client: mqtt.Client, device_id: str, location: str, sensor_id: str, values: dict):
    """Formats and publishes a sensor reading to MQTT."""
    # --- Data Enrichment ---
    # Example: A more accurate dew point calculation
    if "temperature_2" in values and "humidity" in values:
        t = values["temperature_2"]
        rh = values["humidity"]
        # Magnus formula approximation
        b, c = 17.62, 243.12
        gamma = (b * t) / (c + t) + ((rh / 100))
        dew_point = (c * gamma) / (b - gamma)
        values["dew_point"] = round(dew_point, 2)

    # --- Payload Construction ---
    payload = {
        "device_id": device_id,
        "sensor_id": sensor_id,
        "location": location,
        "values": values,
        "timestamp": time.time_ns()
    }
    topic = f"home/{device_id}/{sensor_id}/environment"
    
    # --- Publishing ---
    result = client.publish(topic, json.dumps(payload))
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        logger.info(f"Published reading for {sensor_id} to topic '{topic}'")
    else:
        logger.warning(f"Failed to publish for {sensor_id}. MQTT RC: {result.rc}")


def sleep_until_next_interval(interval_seconds: int):
    """Calculates sleep time to align with the next interval mark."""
    now = datetime.now().timestamp()
    next_timestamp = (now // interval_seconds + 1) * interval_seconds
    sleep_duration = max(0, next_timestamp - now) # Ensure non-negative sleep
    logger.debug(f"Sleeping for {sleep_duration:.2f} seconds.")
    time.sleep(sleep_duration)


# --- Main Application ---
def main():
    """Main application entry point."""
    logger.info("Starting sensor reader service...")

    device_id = CONFIG.get("device_id", "unknown-device")
    location = CONFIG.get("location", "unknown-location")
    read_interval = CONFIG.get("read_interval_seconds", 60)

    sensors = load_sensors(CONFIG)
    if not sensors:
        logger.error("No enabled sensors found in configuration. Exiting.")
        return

    mqtt_client = connect_mqtt(client_id=f"sensor-reader-{device_id}")

    logger.info(f"Starting measurement loop. Interval: {read_interval} seconds.")
    while True:
        for sensor in sensors:
            reading_values = sensor.read()
            if reading_values is not None:
                publish_reading(
                    client=mqtt_client,
                    device_id=device_id,
                    location=location,
                    sensor_id=sensor.id, # We'll need to add an 'id' to our sensor objects
                    values=reading_values
                )
            else:
                logger.warning(f"Failed to get reading from sensor: {sensor.id}")
        
        sleep_until_next_interval(read_interval)

if __name__ == "__main__":
    main()