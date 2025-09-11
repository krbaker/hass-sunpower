"""Test the SunPower integration setup and multi-account support."""

from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from custom_components.sunpower import (
    ENTRY_DATA_CACHE,
    sunpower_fetch,
)
from custom_components.sunpower.const import DOMAIN


@pytest.fixture()
def hass():
    """Create a test Home Assistant instance."""
    from unittest.mock import AsyncMock

    hass_instance = MagicMock()
    hass_instance.config_entries = MagicMock()
    hass_instance.async_add_executor_job = AsyncMock()
    hass_instance.data = {DOMAIN: {}}

    return hass_instance


class TestIntegrationSetup:
    """Test integration setup and multi-account support."""

    def test_sunpower_fetch_with_entry_id(self):
        """Test that sunpower_fetch function properly uses entry-specific caching."""
        from custom_components.sunpower.sunpower import SunPowerMonitor

        # Clear any existing cache
        ENTRY_DATA_CACHE.clear()

        entry_id1 = "test_entry_1"
        entry_id2 = "test_entry_2"

        mock_monitor1 = MagicMock(spec=SunPowerMonitor)
        mock_monitor1.device_list.return_value = {
            "devices": [{"DEVICE_TYPE": "PVS", "SERIAL": "TEST1"}],
        }

        mock_monitor2 = MagicMock(spec=SunPowerMonitor)
        mock_monitor2.device_list.return_value = {
            "devices": [{"DEVICE_TYPE": "PVS", "SERIAL": "TEST2"}],
        }

        # Test the actual sunpower_fetch function
        data1 = sunpower_fetch(mock_monitor1, 120, 60, entry_id1)
        assert entry_id1 in ENTRY_DATA_CACHE
        assert entry_id2 not in ENTRY_DATA_CACHE

        # Verify the function called the monitor
        mock_monitor1.device_list.assert_called_once()

        # Second call should create separate cache for entry2
        data2 = sunpower_fetch(mock_monitor2, 120, 60, entry_id2)
        assert entry_id1 in ENTRY_DATA_CACHE
        assert entry_id2 in ENTRY_DATA_CACHE

        # Verify caches are independent
        cache1 = ENTRY_DATA_CACHE[entry_id1]
        cache2 = ENTRY_DATA_CACHE[entry_id2]

        assert cache1["pvs_sample"] != cache2["pvs_sample"]
        assert data1 != data2

        # Verify the second function called the second monitor
        mock_monitor2.device_list.assert_called_once()

        # Clean up
        ENTRY_DATA_CACHE.clear()

    def test_cache_prevents_unnecessary_api_calls(self):
        """Test that cache prevents API calls within the update interval."""
        from custom_components.sunpower.sunpower import SunPowerMonitor

        # Clear any existing cache
        ENTRY_DATA_CACHE.clear()

        entry_id = "test_entry_cache"
        sunpower_update_interval = 120  # 2 minutes
        sunvault_update_interval = 60  # 1 minute

        # Create mock monitor
        mock_monitor = MagicMock(spec=SunPowerMonitor)
        mock_monitor.device_list.return_value = {
            "devices": [{"DEVICE_TYPE": "PVS", "SERIAL": "TEST123"}],
        }

        # First call - should trigger API call (cache is empty)
        with patch("time.time", return_value=1000.0):  # Mock current time
            data1 = sunpower_fetch(
                mock_monitor,
                sunpower_update_interval,
                sunvault_update_interval,
                entry_id,
            )

        # Verify API was called
        assert mock_monitor.device_list.call_count == 1

        # Verify cache was populated
        assert entry_id in ENTRY_DATA_CACHE
        cache = ENTRY_DATA_CACHE[entry_id]
        assert cache["pvs_sample_time"] == 1000.0
        assert cache["pvs_sample"] == {"devices": [{"DEVICE_TYPE": "PVS", "SERIAL": "TEST123"}]}

        # Second call within cache duration - should NOT trigger API call
        with patch("time.time", return_value=1050.0):  # 50 seconds later (within 120s interval)
            data2 = sunpower_fetch(
                mock_monitor,
                sunpower_update_interval,
                sunvault_update_interval,
                entry_id,
            )

        # Verify API was NOT called again (still 1 call total)
        assert mock_monitor.device_list.call_count == 1

        # Verify same data returned
        assert data1 == data2

        # Verify cache timestamp unchanged (no new fetch)
        assert cache["pvs_sample_time"] == 1000.0

        # Third call after cache expiry - should trigger API call
        with patch("time.time", return_value=1200.0):  # 200 seconds later (beyond 120s interval)
            mock_monitor.device_list.return_value = {
                "devices": [{"DEVICE_TYPE": "PVS", "SERIAL": "TEST456"}],
            }
            data3 = sunpower_fetch(
                mock_monitor,
                sunpower_update_interval,
                sunvault_update_interval,
                entry_id,
            )

        # Verify API was called again (now 2 calls total)
        assert mock_monitor.device_list.call_count == 2

        # Verify cache was updated with new timestamp and data
        assert cache["pvs_sample_time"] == 1200.0
        assert cache["pvs_sample"] == {"devices": [{"DEVICE_TYPE": "PVS", "SERIAL": "TEST456"}]}

        # Verify new data is different
        assert data1 != data3

        # Clean up
        ENTRY_DATA_CACHE.clear()

    def test_entry_cache_isolation(self):
        """Test that multiple entries have properly isolated caches."""
        from custom_components.sunpower.sunpower import SunPowerMonitor

        # Clear any existing cache
        ENTRY_DATA_CACHE.clear()

        entry_id1 = "test_entry_1"
        entry_id2 = "test_entry_2"

        # Create mock monitors for different entries
        mock_monitor1 = MagicMock(spec=SunPowerMonitor)
        mock_monitor1.device_list.return_value = {
            "devices": [{"DEVICE_TYPE": "PVS", "SERIAL": "TEST1"}],
        }

        mock_monitor2 = MagicMock(spec=SunPowerMonitor)
        mock_monitor2.device_list.return_value = {
            "devices": [{"DEVICE_TYPE": "PVS", "SERIAL": "TEST2"}],
        }

        # Fetch data for both entries at same time
        with patch("time.time", return_value=1000.0):
            data1 = sunpower_fetch(mock_monitor1, 120, 60, entry_id1)
            data2 = sunpower_fetch(mock_monitor2, 120, 60, entry_id2)

        # Verify both entries have separate cache entries
        assert entry_id1 in ENTRY_DATA_CACHE
        assert entry_id2 in ENTRY_DATA_CACHE
        assert ENTRY_DATA_CACHE[entry_id1] != ENTRY_DATA_CACHE[entry_id2]

        # Verify different data but same timestamp (called at same time)
        cache1 = ENTRY_DATA_CACHE[entry_id1]
        cache2 = ENTRY_DATA_CACHE[entry_id2]
        assert cache1["pvs_sample_time"] == cache2["pvs_sample_time"] == 1000.0
        assert cache1["pvs_sample"] != cache2["pvs_sample"]
        assert data1 != data2

        # Test that cache behavior is independent for each entry
        with patch("time.time", return_value=1050.0):  # Within cache duration
            # Call entry1 again - should use cache
            data1_cached = sunpower_fetch(mock_monitor1, 120, 60, entry_id1)
            # Call entry2 again - should also use cache
            data2_cached = sunpower_fetch(mock_monitor2, 120, 60, entry_id2)

        # Verify no additional API calls were made (each monitor called once)
        assert mock_monitor1.device_list.call_count == 1
        assert mock_monitor2.device_list.call_count == 1

        # Verify same data returned
        assert data1 == data1_cached
        assert data2 == data2_cached

        # Test cleanup of one entry doesn't affect the other
        ENTRY_DATA_CACHE.pop(entry_id1)
        assert entry_id1 not in ENTRY_DATA_CACHE
        assert entry_id2 in ENTRY_DATA_CACHE

        # Entry2 should still work with its cache
        with patch("time.time", return_value=1080.0):
            data2_still_cached = sunpower_fetch(mock_monitor2, 120, 60, entry_id2)

        assert mock_monitor2.device_list.call_count == 1  # Still only 1 call
        assert data2 == data2_still_cached

        # Clean up
        ENTRY_DATA_CACHE.clear()
