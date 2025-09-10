import logging
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

import sunpower  # noqa: E402

_LOGGER = logging.getLogger(__name__)


@pytest.mark.pvs()
@pytest.mark.skipif(
    os.getenv("PVS") == "MOCK",
    reason="Skipping real PVS tests in MOCK mode",
)
def test_ping():
    """Test we can ping the PVS device."""
    _LOGGER.warning("Pinging PVS at", os.environ["PVS"])
    subprocess.check_call(["ping", "-c", "1", os.environ["PVS"]])


@pytest.mark.pvs()
def test_pvs_device_list(sunpowermonitor):
    """Test we can get a device list from the PVS."""
    result = sunpowermonitor.device_list()
    _LOGGER.debug("Device List: %s", result)
    assert "devices" in result
    assert isinstance(result["devices"], list)
    assert len(result["devices"]) > 0
    _LOGGER.warning(f"Found {len(result['devices'])} devices in device list")


@pytest.mark.ess()
def test_pvs_ess(sunpowermonitor):
    """Test we can get an ESS list from the PVS."""
    result = sunpowermonitor.energy_storage_system_status()
    _LOGGER.debug("ESS data: %s", result)
    assert "errors" in result
    assert "ess_report" in result


@pytest.mark.pvs()
def test_pvs_network(sunpowermonitor):
    """Test we can get an Netork from the PVS."""
    result = sunpowermonitor.network_status()
    _LOGGER.debug("Network data: %s", result)
    assert result is not None


@pytest.mark.pvs()
def test_pvs_parse(sunpowermonitor):
    data = sunpower.convert_sunpower_data(sunpowermonitor.device_list())
    _LOGGER.debug("Converted data: %s", data)
    assert len(data["PVS"]) > 0
    assert len(data["Inverter"]) > 0
    counts = [(x, len(data[x])) for x in ["PVS", "Inverter", "Power Meter"]]
    _LOGGER.warning(f"Found {counts} devices")


@pytest.mark.ess()
def test_ess_parse(sunpowermonitor):
    data = sunpower.convert_ess_data(
        sunpowermonitor.energy_storage_system_status(),
        sunpowermonitor.device_list(),
    )
    _LOGGER.warning(data)
