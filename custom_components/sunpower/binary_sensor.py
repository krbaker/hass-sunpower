"""Support for Sunpower binary sensors."""
import logging

from homeassistant.const import DEVICE_CLASS_POWER
from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import (
    DOMAIN,
    SUNPOWER_COORDINATOR,
    SUNPOWER_DESCRIPTIVE_NAMES,
    PVS_DEVICE_TYPE,
    INVERTER_DEVICE_TYPE,
    METER_DEVICE_TYPE,
    PVS_STATE,
    METER_STATE,
    INVERTER_STATE,
    WORKING_STATE,
)
from .entity import SunPowerPVSEntity, SunPowerMeterEntity, SunPowerInverterEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Sunpower sensors."""
    sunpower_state = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.debug("Sunpower_state: %s", sunpower_state)

    if not SUNPOWER_DESCRIPTIVE_NAMES in config_entry.data:
        config_entry.data[SUNPOWER_DESCRIPTIVE_NAMES] = False
    do_descriptive_names = config_entry.data[SUNPOWER_DESCRIPTIVE_NAMES]

    coordinator = sunpower_state[SUNPOWER_COORDINATOR]
    sunpower_data = coordinator.data

    if PVS_DEVICE_TYPE not in sunpower_data:
        _LOGGER.error("Cannot find PVS Entry")
    else:
        pvs = next(iter(sunpower_data[PVS_DEVICE_TYPE].values()))

        entities = [SunPowerPVSState(coordinator, pvs, do_descriptive_names)]

        if METER_DEVICE_TYPE not in sunpower_data:
            _LOGGER.error("Cannot find any power meters")
        else:
            for data in sunpower_data[METER_DEVICE_TYPE].values():
                entities.append(SunPowerMeterState(coordinator, data, pvs, do_descriptive_names))

        if INVERTER_DEVICE_TYPE not in sunpower_data:
            _LOGGER.error("Cannot find any power inverters")
        else:
            for data in sunpower_data[INVERTER_DEVICE_TYPE].values():
                entities.append(SunPowerInverterState(coordinator, data, pvs, do_descriptive_names))

    async_add_entities(entities, True)


class SunPowerPVSState(SunPowerPVSEntity, BinarySensorEntity):
    """Representation of SunPower PVS Working State"""

    def __init__(self, coordinator, pvs_info, do_descriptive_names):
        super().__init__(coordinator, pvs_info)
        self._do_descriptive_names = do_descriptive_names

    @property
    def name(self):
        """Device Name."""
        if self._do_descriptive_names:
            return "PVS System State"
        else:
            return "System State"

    @property
    def device_class(self):
        """Device Class."""
        return DEVICE_CLASS_POWER

    @property
    def unique_id(self):
        """Device Uniqueid."""
        return f"{self.base_unique_id}_pvs_state"

    @property
    def state(self):
        """Get the current value"""
        return self.coordinator.data[PVS_DEVICE_TYPE][self.base_unique_id][PVS_STATE]

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self.state == WORKING_STATE


class SunPowerMeterState(SunPowerMeterEntity, BinarySensorEntity):
    """Representation of SunPower Meter Working State"""

    def __init__(self, coordinator, meter_info, pvs_info, do_descriptive_names):
        super().__init__(coordinator, meter_info, pvs_info)
        self._do_descriptive_names = do_descriptive_names

    @property
    def name(self):
        """Device Name."""
        if self._do_descriptive_names:
            return f"{self._meter_info['DESCR']} System State"
        else:
            return "System State"

    @property
    def device_class(self):
        """Device Class."""
        return DEVICE_CLASS_POWER

    @property
    def unique_id(self):
        """Device Uniqueid."""
        return f"{self.base_unique_id}_meter_state"

    @property
    def state(self):
        """Get the current value"""
        return self.coordinator.data[METER_DEVICE_TYPE][self.base_unique_id][METER_STATE]

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self.state == WORKING_STATE


class SunPowerInverterState(SunPowerInverterEntity, BinarySensorEntity):
    """Representation of SunPower Inverter Working State"""

    def __init__(self, coordinator, inverter_info, pvs_info, do_descriptive_names):
        super().__init__(coordinator, inverter_info, pvs_info)
        self._do_descriptive_names = do_descriptive_names

    @property
    def name(self):
        """Device Name."""
        if self._do_descriptive_names:
            return f"{self._inverter_info['DESCR']} System State"
        else:
            return "System State"

    @property
    def device_class(self):
        """Device Class."""
        return DEVICE_CLASS_POWER

    @property
    def unique_id(self):
        """Device Uniqueid."""
        return f"{self.base_unique_id}_inverter_state"

    @property
    def state(self):
        """Get the current value"""
        return self.coordinator.data[INVERTER_DEVICE_TYPE][self.base_unique_id][INVERTER_STATE]

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self.state == WORKING_STATE
