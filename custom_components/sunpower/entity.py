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
        serial = self._my_info.get("SERIAL", "UnknownSerial")
        model = self._my_info.get("MODEL", "UnknownModel")
        name = self._my_info.get("DESCR", f"{model} {serial}")
        hw_version = self._my_info.get("HWVER", self._my_info.get("hw_version", "Unknown"))
        sw_version = f"{self._my_info.get("SWVER", "Unknown")} Hardware: {hw_version}"
        device_info = {
            "identifiers": {(DOMAIN, self.base_unique_id)},
            "name": name,
            "manufacturer": "SunPower",
            "model": model,
            "sw_version": sw_version
        }
        if self._parent_info is not None:
            device_info["via_device"] = (
                DOMAIN,
                f"{self._parent_info.get('SERIAL', 'UnknownParent')}",
            )
        return device_info
