import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class Sensor(ABC):
    """Abstract base class for all sensor implementations."""
    def __init__(self, config: dict):
        self.id = config.get("id", "unknown-sensor")
        self.config = config

    @abstractmethod
    def read(self) -> Optional[Dict[str, float]]:
        pass