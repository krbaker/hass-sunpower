"""Support for Sunpower sensors."""
import logging

# from homeassistant.const import TIME_SECONDS, DATA_BYTES

from .const import (
    DOMAIN,
    SUNPOWER_COORDINATOR,
    #    SUNPOWER_DATA,
    #    SUNPOWER_OBJECT,
    PVS_DEVICE_TYPE,
    INVERTER_DEVICE_TYPE,
    METER_DEVICE_TYPE,
    PVS_SENSORS,
    METER_SENSORS,
    INVERTER_SENSORS,
)
from .entity import SunPowerPVSEntity, SunPowerMeterEntity, SunPowerInverterEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Sunpower sensors."""
    sunpower_state = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.error("Sunpower_state: %s", sunpower_state)

    coordinator = sunpower_state[SUNPOWER_COORDINATOR]
    sunpower_data = coordinator.data

    if PVS_DEVICE_TYPE not in sunpower_data:
        _LOGGER.error("Cannot find PVS Entry")
    else:
        pvs = next(iter(sunpower_data[PVS_DEVICE_TYPE].values()))

        entities = []
        for sensor in PVS_SENSORS:
            entities.append(
                SunPowerPVSBasic(
                    coordinator,
                    pvs,
                    PVS_SENSORS[sensor][0],
                    PVS_SENSORS[sensor][1],
                    PVS_SENSORS[sensor][2],
                    PVS_SENSORS[sensor][3],
                )
            )

        if METER_DEVICE_TYPE not in sunpower_data:
            _LOGGER.error("Cannot find any power meters")
        else:
            for data in sunpower_data[METER_DEVICE_TYPE].values():
                for sensor in METER_SENSORS:
                    entities.append(
                        SunPowerMeterBasic(
                            coordinator,
                            data,
                            pvs,
                            METER_SENSORS[sensor][0],
                            METER_SENSORS[sensor][1],
                            METER_SENSORS[sensor][2],
                            METER_SENSORS[sensor][3],
                        )
                    )

        if INVERTER_DEVICE_TYPE not in sunpower_data:
            _LOGGER.error("Cannot find any power inverters")
        else:
            for data in sunpower_data[INVERTER_DEVICE_TYPE].values():
                for sensor in INVERTER_SENSORS:
                    entities.append(
                        SunPowerInverterBasic(
                            coordinator,
                            data,
                            pvs,
                            INVERTER_SENSORS[sensor][0],
                            INVERTER_SENSORS[sensor][1],
                            INVERTER_SENSORS[sensor][2],
                            INVERTER_SENSORS[sensor][3],
                        )
                    )

    async_add_entities(entities, True)


class SunPowerPVSBasic(SunPowerPVSEntity):
    """Representation of SunPower PVS Stat"""

    def __init__(self, coordinator, pvs_info, field, title, unit, icon):
        """Initialize the sensor."""
        super().__init__(coordinator, pvs_info)
        self._title = title
        self._field = field
        self._unit = unit
        self._icon = icon

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def name(self):
        """Device Name."""
        return self._title

    @property
    def unique_id(self):
        """Device Uniqueid."""
        return f"{self.base_unique_id}_pvs_{self._field}"

    @property
    def state(self):
        """Get the current value"""
        return self.coordinator.data[PVS_DEVICE_TYPE][self.base_unique_id][self._field]


class SunPowerMeterBasic(SunPowerMeterEntity):
    """Representation of SunPower Meter Stat"""

    def __init__(self, coordinator, meter_info, pvs_info, field, title, unit, icon):
        """Initialize the sensor."""
        super().__init__(coordinator, meter_info, pvs_info)
        self._title = title
        self._field = field
        self._unit = unit
        self._icon = icon

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def name(self):
        """Device Name."""
        return self._title

    @property
    def unique_id(self):
        """Device Uniqueid."""
        return f"{self.base_unique_id}_pvs_{self._field}"

    @property
    def state(self):
        """Get the current value"""
        return self.coordinator.data[METER_DEVICE_TYPE][self.base_unique_id][self._field]


class SunPowerInverterBasic(SunPowerInverterEntity):
    """Representation of SunPower Meter Stat"""

    def __init__(self, coordinator, inverter_info, pvs_info, field, title, unit, icon):
        """Initialize the sensor."""
        super().__init__(coordinator, inverter_info, pvs_info)
        self._title = title
        self._field = field
        self._unit = unit
        self._icon = icon

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def name(self):
        """Device Name."""
        return self._title

    @property
    def unique_id(self):
        """Device Uniqueid."""
        return f"{self.base_unique_id}_pvs_{self._field}"

    @property
    def state(self):
        """Get the current value"""
        return self.coordinator.data[INVERTER_DEVICE_TYPE][self.base_unique_id][self._field]
