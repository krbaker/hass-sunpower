"""The Sunpower integration base entity."""

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class SunPowerEntity(CoordinatorEntity):
    def __init__(self, coordinator, my_info, parent_info, entry_id=None):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._my_info = my_info
        self._parent_info = parent_info
        self._entry_id = entry_id
        self.base_unique_id = self._my_info.get("SERIAL", "")

    @property
    def device_info(self):
        serial = self._my_info.get("SERIAL", "UnknownSerial")
        model = self._my_info.get("MODEL", "UnknownModel")
        name = self._my_info.get("DESCR", f"{model} {serial}")
        hw_version = self._my_info.get("HWVER", self._my_info.get("hw_version", "Unknown"))
        sw_version = self._my_info.get("SWVER", "Unknown")
        version = f"{sw_version} Hardware: {hw_version}"
        # Include entry_id in device identifiers to prevent conflicts between multiple accounts
        device_identifier = (
            f"{self._entry_id}_{self.base_unique_id}" if self._entry_id else self.base_unique_id
        )
        device_info = {
            "identifiers": {(DOMAIN, device_identifier)},
            "name": name,
            "manufacturer": "SunPower",
            "model": model,
            "sw_version": version,
        }
        if self._parent_info is not None:
            parent_identifier = (
                f"{self._entry_id}_{self._parent_info.get('SERIAL', 'UnknownParent')}"
                if self._entry_id
                else self._parent_info.get("SERIAL", "UnknownParent")
            )
            device_info["via_device"] = (
                DOMAIN,
                parent_identifier,
            )
        return device_info
