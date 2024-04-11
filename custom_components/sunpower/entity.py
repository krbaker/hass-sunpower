"""The Sunpower integration base entity."""

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

class SunPowerEntity(CoordinatorEntity):
    def __init__(self, coordinator, my_info, parent_info):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._my_info = my_info
        self._parent_info = parent_info
        self.base_unique_id = self._my_info.get("SERIAL", "")
    
    @property
    def device_info(self):
        device_info = {
            "identifiers": {(DOMAIN, self.base_unique_id)},
            "name": f"{self._my_info.get('DESCR', f"{self._my_info.get('MODEL', 'UnknownModel')} {self._my_info.get('SERIAL', 'UnknownSerial')}")}",
            "manufacturer": "SunPower",
            "model": f"{self._my_info.get('MODEL', 'UnknownModel')}",
            "sw_version": f"{self._my_info.get('SWVER', 'UnknownVersion')}",
        }
        if self._parent_info is not None:
            device_info["via_device"] = f"{self._parent_info.get('SERIAL', 'UnknownParent')}"
        return device_info


class SunPowerPVSEntity(CoordinatorEntity):
    """Base class for sunpower pvs entities."""

    def __init__(self, coordinator, pvs_info):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.base_unique_id = pvs_info["SERIAL"]
        self._pvs_info = pvs_info

    @property
    def device_info(self):
        """Sunpower PVS device info."""
        device_info = {
            "identifiers": {(DOMAIN, self.base_unique_id)},
            "name": "{} {}".format(self._pvs_info["MODEL"], self._pvs_info["SERIAL"]),
            "manufacturer": "SunPower",
            "model": self._pvs_info["MODEL"],
            "sw_version": "{}, Hardware: {}".format(
                self._pvs_info["SWVER"], self._pvs_info["HWVER"]
            ),
        }
        return device_info


class SunPowerMeterEntity(CoordinatorEntity):
    """Base class for sunpower meter entities."""

    def __init__(self, coordinator, meter_info, pvs_info):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.base_unique_id = meter_info["SERIAL"]
        self._pvs_info = pvs_info
        self._meter_info = meter_info

    @property
    def device_info(self):
        """Sunpower Inverter device info."""
        device_info = {
            "identifiers": {(DOMAIN, self.base_unique_id)},
            "name": self._meter_info["DESCR"],
            "manufacturer": "SunPower",
            "model": self._meter_info["MODEL"],
            "sw_version": self._meter_info["SWVER"],
            "via_device": (DOMAIN, self._pvs_info["SERIAL"]),
        }
        return device_info


class SunPowerInverterEntity(CoordinatorEntity):
    """Base class for sunpower inverter entities."""

    def __init__(self, coordinator, inverter_info, pvs_info):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.base_unique_id = inverter_info["SERIAL"]
        self._pvs_info = pvs_info
        self._inverter_info = inverter_info

    @property
    def device_info(self):
        """Sunpower Inverter device info."""
        device_info = {
            "identifiers": {(DOMAIN, self.base_unique_id)},
            "name": self._inverter_info["DESCR"],
            "manufacturer": self._inverter_info["TYPE"],
            "model": self._inverter_info["MODEL"],
            "sw_version": self._inverter_info["SWVER"],
            "via_device": (DOMAIN, self._pvs_info["SERIAL"]),
        }
        return device_info
