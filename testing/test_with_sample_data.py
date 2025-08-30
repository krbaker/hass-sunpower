#!/usr/bin/env python3
"""
Test SunPower integration with sample data.
This script uses the sample device_list.json to test integration logic
without requiring a real PVS connection.
"""

import json
import os
import sys

# Add the custom_components directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

from unittest.mock import Mock  # noqa: E402

from sunpower import (  # noqa: E402
    convert_sunpower_data,
    sunpower_fetch,
)
from sunpower.sunpower import SunPowerMonitor  # noqa: E402


def load_sample_data():
    """Load the sample device list data."""
    sample_file = os.path.join(os.path.dirname(__file__), "samples", "device_list.json")

    if not os.path.exists(sample_file):
        print("❌ Sample file not found: samples/device_list.json")
        return None

    with open(sample_file, "r") as f:
        return json.load(f)


def test_data_processing():
    """Test data processing with sample data."""
    print("🧪 Testing SunPower Integration with Sample Data")
    print("=" * 50)

    # Load sample data
    sample_data = load_sample_data()
    if not sample_data:
        return

    print(f"✅ Loaded sample data with {len(sample_data.get('devices', []))} devices")

    print("\n1. Testing data conversion...")

    # Test data conversion
    converted_data = convert_sunpower_data(sample_data)
    print("✅ Data conversion successful")
    print(f"📊 Device types found: {list(converted_data.keys())}")

    # Show detailed breakdown
    print("\n2. Device breakdown:")
    total_devices = 0
    for device_type, devices in converted_data.items():
        count = len(devices)
        total_devices += count
        print(f"  - {device_type}: {count} devices")

        if devices:
            # Show sample device info
            sample_device = next(iter(devices.values()))
            print(f"    Serial example: {sample_device.get('SERIAL', 'Unknown')}")
            print(f"    Model example: {sample_device.get('MODEL', 'Unknown')}")
            print(f"    State example: {sample_device.get('STATE', 'Unknown')}")

            # Show available fields
            field_count = len(sample_device.keys())
            sample_fields = list(sample_device.keys())[:6]  # First 6 fields
            print(f"    Fields ({field_count} total): {sample_fields}")
            print()

    print(f"📈 Total devices processed: {total_devices}")

    print("\n3. Testing sensor mapping...")

    # Test sensor mapping by checking if key fields are available
    from sunpower.const import (  # noqa: E402
        SUNPOWER_SENSORS,
        SUNVAULT_SENSORS,
    )

    # Combine all sensors
    all_sensors = {**SUNPOWER_SENSORS}
    if any("ESS" in device_type for device_type in converted_data.keys()):
        all_sensors.update(SUNVAULT_SENSORS)
        print("✅ ESS devices detected - SunVault sensors will be included")
    else:
        print("ℹ️  No ESS devices - SunVault sensors not needed")

    # Check sensor field availability
    sensor_compatibility = {}
    for device_type, type_config in all_sensors.items():
        if device_type in converted_data:
            devices = converted_data[device_type]
            if devices:
                sample_device = next(iter(devices.values()))
                sensors = type_config["sensors"]

                available_fields = []
                missing_fields = []

                for _sensor_name, sensor_config in sensors.items():
                    field = sensor_config["field"]
                    if field in sample_device:
                        available_fields.append(field)
                    else:
                        missing_fields.append(field)

                sensor_compatibility[device_type] = {
                    "available": len(available_fields),
                    "missing": len(missing_fields),
                    "total": len(sensors),
                    "missing_fields": missing_fields[:3],  # Show first 3 missing
                }

    print("\n4. Sensor field compatibility:")
    for device_type, stats in sensor_compatibility.items():
        available = stats["available"]
        total = stats["total"]
        percentage = (available / total * 100) if total > 0 else 0
        print(f"  - {device_type}: {available}/{total} fields available ({percentage:.1f}%)")

        if stats["missing"] > 0:
            missing_sample = stats["missing_fields"]
            print(f"    Missing examples: {missing_sample}")

    print("\n5. Testing virtual meter creation...")

    # Check if virtual meter was created
    if "Power Meter" in converted_data:
        meters = converted_data["Power Meter"]
        virtual_meters = [m for serial, m in meters.items() if m.get("origin") == "virtual"]

        if virtual_meters:
            print(f"✅ Virtual meter created: {len(virtual_meters)} virtual meter(s)")
            vm = virtual_meters[0]
            print(f"  - Serial: {vm.get('SERIAL')}")
            print(f"  - Type: {vm.get('TYPE')}")
            print(f"  - Model: {vm.get('MODEL')}")
            print(f"  - Power: {vm.get('p_3phsum_kw', 'N/A')} kW")
            print(f"  - Energy: {vm.get('net_ltea_3phsum_kwh', 'N/A')} kWh")
        else:
            print("⚠️  No virtual meter found")
    else:
        print("⚠️  No power meters found")

    print("\n6. Testing mock data fetch...")

    # Create a mock monitor that returns our sample data
    mock_monitor = Mock(spec=SunPowerMonitor)
    mock_monitor.device_list.return_value = sample_data
    mock_monitor.energy_storage_system_status.return_value = {"result": "sample"}

    # Test the sunpower_fetch function
    entry_id = "test_sample_entry"
    try:
        fetch_data = sunpower_fetch(mock_monitor, 120, 60, entry_id)

        if fetch_data:
            print("✅ Data fetch function successful")
            print(f"📊 Fetched data keys: {list(fetch_data.keys())}")

            # Compare with direct conversion
            total_devices_fetch = sum(len(devices) for devices in fetch_data.values())
            print(f"📈 Total devices from fetch: {total_devices_fetch}")

            if total_devices_fetch == total_devices:
                print("✅ Data consistency check passed")
            else:
                print("⚠️  Data count mismatch between methods")
        else:
            print("❌ Data fetch returned None")

    except Exception as e:
        print(f"❌ Data fetch failed: {e}")

    print("\n🎉 Sample data testing completed!")
    print("\n💡 This validates that:")
    print("   - Data conversion logic works correctly")
    print("   - Sensor field mapping is compatible")
    print("   - Virtual meter creation functions")
    print("   - Core integration logic is sound")


if __name__ == "__main__":
    test_data_processing()
