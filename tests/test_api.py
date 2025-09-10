#!/usr/bin/env python3
"""
Simple script to test the SunPower API client directly.
Set PVS_HOST environment variable or edit the host below.
"""

import asyncio
import os
import sys
from pprint import pprint

# Add the custom_components directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

from sunpower.sunpower import (  # noqa: E402
    ConnectionException,
    ParseException,
    SunPowerMonitor,
)


async def test_api():
    """Test the SunPower API client."""
    # Change this to your PVS IP address
    host = os.getenv("PVS_HOST", "172.27.153.1")  # Default PVS IP for NAT setup

    print(f"Testing SunPower API connection to {host}")
    print("-" * 50)

    monitor = SunPowerMonitor(host)

    try:
        print("1. Testing network status...")
        network_status = monitor.network_status()
        print("✅ Network status successful")
        pprint(network_status)
        print()

    except (ConnectionException, ParseException) as e:
        print(f"❌ Network status failed: {e}")
        print("Check that:")
        print("- PVS is accessible at the IP address")
        print("- Network connectivity is working")
        print("- PVS management interface is enabled")
        return

    try:
        print("2. Testing device list...")
        device_list = monitor.device_list()
        print("✅ Device list successful")
        print(f"Found {len(device_list.get('devices', []))} devices")

        # Show device summary
        device_types = {}
        for device in device_list.get("devices", []):
            device_type = device.get("DEVICE_TYPE", "Unknown")
            device_types[device_type] = device_types.get(device_type, 0) + 1

        print("Device breakdown:")
        for device_type, count in device_types.items():
            print(f"  - {device_type}: {count}")
        print()

    except (ConnectionException, ParseException) as e:
        print(f"❌ Device list failed: {e}")
        print()

    try:
        print("3. Testing energy storage system status...")
        ess_status = monitor.energy_storage_system_status()
        print("✅ ESS status successful")
        pprint(ess_status)
        print()

    except (ConnectionException, ParseException) as e:
        print(f"❌ ESS status failed (this is normal if no ESS): {e}")
        print()


if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_api())
