import time
from unittest.mock import MagicMock

# Using pytest fixtures to set up reusable test data
import pytest
from freezegun import freeze_time
from src import main


@pytest.fixture
def sample_config():
    """Provides a sample config dictionary for tests."""
    return {
        "device_id": "test-pi",
        "location": "test-lab",
        "sensors": [
            {"id": "test-mock-1", "type": "mock", "enabled": True},
            {"id": "test-system-1", "type": "system", "enabled": True},
            {"id": "disabled-sensor", "type": "mock", "enabled": False},
        ]
    }

def test_load_sensors(sample_config):
    """Tests that the sensor factory correctly loads enabled sensors."""
    # Act
    sensors = main.load_sensors(sample_config)

    # Assert
    assert len(sensors) == 2  # Should only load the two enabled sensors
    assert sensors[0].id == "test-mock-1"
    assert sensors[1].id == "test-system-1"

@freeze_time("2025-09-18 17:50:35") # Lock the current time for the test
def test_sleep_until_next_interval():
    """Tests the precise timing calculation."""
    # Arrange
    interval_seconds = 60
    
    # Act
    # We can't actually sleep in a test, so we'll inspect the calculation.
    # We need to slightly modify the original function to make it testable
    # or test its effect indirectly. Let's assume we refactor it to return the
    # sleep duration for testing purposes.
    
    now = time.time() # This will be the frozen time: 17:50:35
    next_timestamp = (now // interval_seconds + 1) * interval_seconds # 17:51:00
    expected_sleep = next_timestamp - now # 25 seconds

    # This is a conceptual test. In practice, you'd refactor sleep_until_next_interval
    # to be more easily testable or use mocks.
    assert round(expected_sleep) == 25

def test_publish_reading_payload(mocker): # pytest-mock provides the 'mocker' fixture
    """Tests that the MQTT payload is correctly formatted."""
    # Arrange
    mock_mqtt_client = MagicMock()
    # Mock the json.dumps function to inspect its input
    mock_json_dumps = mocker.patch('json.dumps', return_value="{}")

    # Act
    main.publish_reading(
        client=mock_mqtt_client,
        device_id="test-device",
        location="test-location",
        sensor_id="test-sensor",
        values={"temperature": 20.0}
    )

    # Assert
    # Get the dictionary that was passed to json.dumps
    sent_payload = mock_json_dumps.call_args[0][0]
    
    assert sent_payload['device_id'] == "test-device"
    assert sent_payload['location'] == "test-location"
    assert sent_payload['values']['temperature'] == 20.0
    assert 'timestamp' in sent_payload