"""Support for Sunpower binary sensors."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import (
    DOMAIN,
    PVS_DEVICE_TYPE,
    SUNPOWER_BINARY_SENSORS,
    SUNPOWER_COORDINATOR,
    SUNPOWER_DESCRIPTIVE_NAMES,
    SUNPOWER_ESS,
    SUNVAULT_BINARY_SENSORS,
)
from .entity import SunPowerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Sunpower sensors."""
    sunpower_state = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.debug("Sunpower_state: %s", sunpower_state)

    if SUNPOWER_DESCRIPTIVE_NAMES not in config_entry.data:
        config_entry.data[SUNPOWER_DESCRIPTIVE_NAMES] = False
    do_descriptive_names = config_entry.data[SUNPOWER_DESCRIPTIVE_NAMES]
    do_ess = config_entry.data[SUNPOWER_ESS]

    coordinator = sunpower_state[SUNPOWER_COORDINATOR]
    sunpower_data = coordinator.data

    if PVS_DEVICE_TYPE not in sunpower_data:
        _LOGGER.error("Cannot find PVS Entry")
    else:
        entities = []

        pvs = next(iter(sunpower_data[PVS_DEVICE_TYPE].values()))

        BINARY_SENSORS = SUNPOWER_BINARY_SENSORS
        if do_ess:
            BINARY_SENSORS.update(SUNVAULT_BINARY_SENSORS)

        for device_type in BINARY_SENSORS:
            if device_type not in sunpower_data:
                _LOGGER.error(f"Cannot find any {device_type}")
                continue
            unique_id = BINARY_SENSORS[device_type]["unique_id"]
            sensors = BINARY_SENSORS[device_type]["sensors"]
            for index, sensor_data in enumerate(sunpower_data[device_type].values()):
                for sensor_name in sensors:
                    sensor = sensors[sensor_name]
                    sensor_type = (
                        "" if not do_descriptive_names else f"{sensor_data.get('TYPE', '')} "
                    )
                    sensor_description = (
                        "" if not do_descriptive_names else f"{sensor_data.get('DESCR', '')} "
                    )
                    text_sunpower = "" if not do_descriptive_names else "SunPower "
                    text_sunvault = "" if not do_descriptive_names else "SunVault "
                    text_pvs = "" if not do_descriptive_names else "PVS "
                    sensor_index = "" if not do_descriptive_names else f"{index + 1} "
                    sunpower_sensor = SunPowerState(
                        coordinator=coordinator,
                        my_info=sensor_data,
                        parent_info=pvs if device_type != PVS_DEVICE_TYPE else None,
                        id_code=unique_id,
                        device_type=device_type,
                        field=sensor["field"],
                        title=sensor["title"].format(
                            index=sensor_index,
                            TYPE=sensor_type,
                            DESCR=sensor_description,
                            SUN_POWER=text_sunpower,
                            SUN_VAULT=text_sunvault,
                            PVS=text_pvs,
                        ),
                        device_class=sensor["device"],
                        on_value=sensor["on_value"],
                    )
                    entities.append(sunpower_sensor)

    async_add_entities(entities, True)


class SunPowerState(SunPowerEntity, BinarySensorEntity):
    """Representation of SunPower Meter Working State"""

    def __init__(
        self,
        coordinator,
        my_info,
        parent_info,
        id_code,
        device_type,
        field,
        title,
        device_class,
        on_value,
    ):
        super().__init__(coordinator, my_info, parent_info)
        self._id_code = id_code
        self._device_type = device_type
        self._title = title
        self._field = field
        self._my_device_class = device_class
        self._on_value = on_value

    @property
    def name(self):
        """Device Name."""
        return self._title

    @property
    def device_class(self):
        """Device Class."""
        return self._my_device_class

    @property
    def unique_id(self):
        """Device Uniqueid.
        https://developers.home-assistant.io/docs/entity_registry_index/#unique-id
        Should not include the domain, home assistant does that for us
        base_unique_id is the serial number of the device (Inverter, PVS, Meter etc)
        "_pvs_" just as a divider - in case we start pulling data from some other source
        _field is the field within the data that this came from which is a dict so there is only one
        Updating this format is a breaking change and should be called out if changed in a PR
        """
        return f"{self.base_unique_id}_pvs_{self._field}"


    @property
    def state(self):
        """Get the current value"""
        return self.coordinator.data[self._device_type][self.base_unique_id][self._field]

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self.state == self._on_value
