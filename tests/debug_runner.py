#!/usr/bin/env python3
"""
Debug runner for the SunPower integration.
This script simulates how Home Assistant would load and run the integration.
"""

import asyncio
import logging
import os
import sys

# Add the custom_components directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

from sunpower import (  # noqa: E402
    convert_sunpower_data,
    sunpower_fetch,
)
from sunpower.sunpower import SunPowerMonitor  # noqa: E402

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def debug_integration():
    """Debug the SunPower integration."""
    host = os.getenv("PVS_HOST", "172.27.153.1")

    print("🔧 Starting SunPower Integration Debug")
    print(f"📡 PVS Host: {host}")
    print("-" * 50)

    try:
        print("1. Testing SunPower API client...")
        monitor = SunPowerMonitor(host)

        # Test basic connectivity
        network_status = monitor.network_status()
        print("✅ PVS connectivity successful")
        interface_count = len(
            network_status.get("networkstatus", {}).get("interfaces", []),
        )
        print(f"📊 Network interfaces found: {interface_count}")

        # Test data fetching
        device_data = monitor.device_list()
        print(f"✅ Retrieved {len(device_data.get('devices', []))} devices")

        # Test data conversion
        converted_data = convert_sunpower_data(device_data)
        print("✅ Data conversion successful")
        print(f"📊 Device types found: {list(converted_data.keys())}")

        print("\n2. Testing data processing...")

        # Show device breakdown
        for device_type, devices in converted_data.items():
            print(f"  - {device_type}: {len(devices)} devices")
            if devices:
                sample_device = next(iter(devices.values()))
                sample_fields = list(sample_device.keys())[:8]  # First 8 fields
                print(f"    Sample fields: {sample_fields}")

        print("\n3. Testing data fetch function...")

        # Test the sunpower_fetch function directly
        entry_id = "test_entry_123"
        fetch_data = sunpower_fetch(monitor, 120, 60, entry_id)

        if fetch_data:
            print("✅ Data fetch function successful")
            print(f"📊 Fetched data keys: {list(fetch_data.keys())}")

            # Show data summary
            total_devices = sum(len(devices) for devices in fetch_data.values())
            print(f"📈 Total devices processed: {total_devices}")

        print("\n4. Testing ESS functionality...")

        try:
            ess_data = monitor.energy_storage_system_status()
            print("✅ ESS data retrieval successful")
            print(f"📊 ESS result: {ess_data.get('result', 'Unknown')}")
        except Exception as e:
            print(f"⚠️  ESS data failed (normal if no ESS): {e}")

        print("\n🎉 All core functionality tests completed successfully!")
        print("\n💡 To test full Home Assistant integration:")
        print("   1. Install this integration in Home Assistant")
        print("   2. Use the configuration flow to set up your PVS")
        print("   3. Check entity registry for created sensors")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        logger.exception("Full error details:")

        # Provide helpful troubleshooting info
        print("\n🔍 Troubleshooting:")
        print("- Check that PVS_HOST environment variable is set correctly")
        print("- Verify PVS is accessible on your network")
        print("- Ensure PVS management interface is connected")
        print(f"- Try: curl 'http://{host}/cgi-bin/dl_cgi?Command=Get_Comm'")

    print("\n✅ Debug session completed")


if __name__ == "__main__":
    print("🚀 SunPower Integration Debugger")
    print("=" * 50)
    print("This script helps debug the SunPower integration outside of Home Assistant.")
    print("Set the PVS_HOST environment variable to your PVS IP address.")
    print("Example: export PVS_HOST=192.168.1.100")
    print("")

    # Run the debug session
    asyncio.run(debug_integration())
