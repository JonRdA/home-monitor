import logging
import logging.config
import os


def setup_logging():
    """
    Configures logging for the application using an external .conf file.
    """
    config_file = os.path.join(os.path.dirname(__file__), '..', 'logging.conf')
    if os.path.exists(config_file):
        logging.config.fileConfig(config_file)
        logging.getLogger(__name__).info(f"Logging configured from {config_file}")
    else:
        # Fallback to basic config if file is missing
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.getLogger(__name__).warning(f"logging.conf not found. Using basicConfig.")