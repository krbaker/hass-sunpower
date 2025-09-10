import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

import sunpower  # noqa: E402

DEVICE_LIST_SAMPLE = os.path.join(
    os.path.dirname(__file__),
    "samples",
    "ess_device_list.json",
)
DEVICE_LIST_JSON = json.load(open(DEVICE_LIST_SAMPLE))
ESS_STATUS_SAMPLE = os.path.join(
    os.path.dirname(__file__),
    "samples",
    "ess_status.json",
)
ESS_STATUS_JSON = json.load(open(ESS_STATUS_SAMPLE))


@pytest.fixture()
def sunpowermonitor(mocker):
    """SunPower Monitor fixture."""
    if os.getenv("PVS") == "MOCK":
        monitor = sunpower.SunPowerMonitor(None)
        mocker.patch.object(monitor, "device_list", return_value=DEVICE_LIST_JSON)
        mocker.patch.object(
            monitor,
            "energy_storage_system_status",
            return_value=ESS_STATUS_JSON,
        )
        mocker.patch.object(monitor, "network_status", return_value="Something")
        yield monitor
        return
    elif os.getenv("PVS"):
        monitor = sunpower.SunPowerMonitor(os.getenv("PVS"))
        yield monitor
    else:
        raise Exception("PVS environment variable not set")
