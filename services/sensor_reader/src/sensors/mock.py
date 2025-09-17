import random
from typing import Dict, Optional

from .abstract_sensor import Sensor


class MockSensor(Sensor):
    """A mock sensor that generates random data for development."""

    def __init__(self, config: dict):
        super().__init__(config)

    def read(self) -> Optional[Dict[str, float]]:
        """Generates random environmental data."""
        print("INFO: Reading from MockSensor...")
        data = {
            "temperature_1": round(random.uniform(18.0, 25.0), 2),
            "temperature_2": round(random.uniform(18.0, 25.0), 2),
            "pressure": round(random.uniform(980.0, 1030.0), 2),
            "humidity": round(random.uniform(40.0, 65.0), 2),
        }
        return data