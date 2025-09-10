import os
import subprocess

import pytest


@pytest.mark.pvs()
@pytest.mark.skipif(
    os.getenv("PVS") == "MOCK",
    reason="Skipping real PVS tests in MOCK mode",
)
def test_ping():
    """Test we can ping the PVS device."""
    print("Pinging PVS at", os.environ["PVS"])
    subprocess.check_call(["ping", "-c", "1", os.environ["PVS"]])


@pytest.mark.pvs()
def test_pvs_device_list(sunpowermonitor):
    """Test we can get a device list from the PVS."""
    result = sunpowermonitor.device_list()
    assert "devices" in result
    assert isinstance(result["devices"], list)
    assert len(result["devices"]) > 0


@pytest.mark.pvs()
def test_pvs_ess(sunpowermonitor):
    """Test we can get an ESS list from the PVS."""
    result = sunpowermonitor.energy_storage_system_status()
    assert "errors" in result
    assert "ess_report" in result


@pytest.mark.pvs()
def test_pvs_network(sunpowermonitor):
    """Test we can get an Netork from the PVS."""
    result = sunpowermonitor.network_status()
    assert result is not None
