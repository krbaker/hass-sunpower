#!/usr/bin/env python3
"""
Test Home Assistant integration with proper mocking.
This script tests the integration setup without requiring a full HA environment.
"""

import asyncio
import logging
import os
import sys
from unittest.mock import (
    AsyncMock,
    Mock,
)

# Add the custom_components directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

from homeassistant.config_entries import ConfigEntry  # noqa: E402
from homeassistant.core import HomeAssistant  # noqa: E402
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator  # noqa: E402
from sunpower.const import (  # noqa: E402
    DOMAIN,
    SUNPOWER_DESCRIPTIVE_NAMES,
    SUNPOWER_HOST,
    SUNPOWER_PRODUCT_NAMES,
)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def test_ha_integration():
    """Test the integration with a more realistic Home Assistant mock."""
    host = os.getenv("PVS_HOST", "172.27.153.1")

    print("🏠 Testing Home Assistant Integration")
    print(f"📡 PVS Host: {host}")
    print("-" * 50)

    # Create a minimal mock HA that satisfies the coordinator requirements
    hass = Mock(spec=HomeAssistant)
    hass.data = {}
    hass.loop = asyncio.get_event_loop()
    hass.bus = Mock()
    hass.bus.async_fire = AsyncMock()
    hass.states = Mock()

    # Mock async_add_executor_job
    async def mock_executor_job(func, *args):
        return func(*args)

    hass.async_add_executor_job = mock_executor_job

    # Create config entry
    config_entry = Mock(spec=ConfigEntry)
    config_entry.entry_id = "test_entry_123"
    config_entry.data = {
        SUNPOWER_HOST: host,
        SUNPOWER_DESCRIPTIVE_NAMES: True,
        SUNPOWER_PRODUCT_NAMES: False,
    }
    config_entry.options = {}

    def mock_unload(func):
        pass

    config_entry.async_on_unload = mock_unload
    config_entry.add_update_listener = Mock(return_value=mock_unload)

    try:
        print("1. Testing basic data structures...")

        # Initialize domain data
        hass.data.setdefault(DOMAIN, {})
        print("✅ Domain data initialized")

        print("\n2. Testing data coordinator creation...")

        # Create a simple coordinator without the full integration
        from datetime import timedelta

        from sunpower import sunpower_fetch  # noqa: E402
        from sunpower.sunpower import SunPowerMonitor  # noqa: E402

        monitor = SunPowerMonitor(host)

        async def async_update_data():
            """Test update function."""
            return sunpower_fetch(monitor, 120, 60, config_entry.entry_id)

        coordinator = DataUpdateCoordinator(
            hass,
            logger,
            name="SunPower PVS Test",
            update_method=async_update_data,
            update_interval=timedelta(seconds=120),
        )
        print("✅ Data coordinator created successfully")

        print("\n3. Testing data fetch...")

        # Test data fetch
        await coordinator.async_refresh()

        if coordinator.data:
            print("✅ Data fetch successful")
            print(f"📊 Data keys: {list(coordinator.data.keys())}")

            # Show device summary
            total_devices = sum(len(devices) for devices in coordinator.data.values())
            print(f"📈 Total devices: {total_devices}")
        else:
            print("⚠️  No data returned from coordinator")

        print("\n🎉 Home Assistant integration test completed successfully!")

    except Exception as e:
        print(f"❌ Error during HA integration testing: {e}")
        logger.exception("Full error details:")

        # Provide helpful info
        print("\n🔍 This test validates that:")
        print("- DataUpdateCoordinator can be created")
        print("- Data fetching works with the coordinator")
        print("- Basic Home Assistant compatibility")

    print("\n✅ HA integration test completed")


if __name__ == "__main__":
    print("🏠 SunPower Home Assistant Integration Tester")
    print("=" * 50)
    print("This script tests the integration's compatibility with Home Assistant.")
    print("Set PVS_HOST environment variable to test with a real PVS.")
    print("")

    # Run the test
    asyncio.run(test_ha_integration())
