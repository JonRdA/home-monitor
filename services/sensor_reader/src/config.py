import logging
import os

import yaml

logger = logging.getLogger(__name__)

def load_config():
    """Loads configuration from a YAML file."""
    config_path = os.environ.get("CONFIG_PATH", "config.yml")
    logger.info(f"Loading configuration from {config_path}")
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {config_path}. Exiting.")
        exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}. Exiting.")
        exit(1)

# Load config at module import
CONFIG = load_config()

# MQTT settings can still be overridden by environment variables for flexibility
MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "localhost")