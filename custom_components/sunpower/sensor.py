"""Support for Sunpower sensors."""
import logging

from homeassistant.components.sensor import SensorEntity

from .const import (
    DOMAIN,
    SUNPOWER_COORDINATOR,
    SUNPOWER_DESCRIPTIVE_NAMES,
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

        entities = []
        for sensor in PVS_SENSORS:
            if do_descriptive_names:
                title = f"{pvs['DEVICE_TYPE']} {PVS_SENSORS[sensor][1]}"
            else:
                title = PVS_SENSORS[sensor][1]
            spb = SunPowerPVSBasic(
                coordinator,
                pvs,
                PVS_SENSORS[sensor][0],
                title,
                PVS_SENSORS[sensor][2],
                PVS_SENSORS[sensor][3],
                PVS_SENSORS[sensor][4],
                PVS_SENSORS[sensor][5],
            )
            try:
                spb.native_value
                entities.append(spb)
            except KeyError:
                pass

        if METER_DEVICE_TYPE not in sunpower_data:
            _LOGGER.error("Cannot find any power meters")
        else:
            for data in sunpower_data[METER_DEVICE_TYPE].values():
                for sensor in METER_SENSORS:
                    if do_descriptive_names:
                        title = f"{data['DESCR']} {METER_SENSORS[sensor][1]}"
                    else:
                        title = METER_SENSORS[sensor][1]
                    smb = SunPowerMeterBasic(
                        coordinator,
                        data,
                        pvs,
                        METER_SENSORS[sensor][0],
                        title,
                        METER_SENSORS[sensor][2],
                        METER_SENSORS[sensor][3],
                        METER_SENSORS[sensor][4],
                        METER_SENSORS[sensor][5],
                    )
                    try:
                        smb.native_value
                        entities.append(smb)
                    except KeyError:
                        pass

        if INVERTER_DEVICE_TYPE not in sunpower_data:
            _LOGGER.error("Cannot find any power inverters")
        else:
            for data in sunpower_data[INVERTER_DEVICE_TYPE].values():
                for sensor in INVERTER_SENSORS:
                    if do_descriptive_names:
                        title = f"{data['DESCR']} {INVERTER_SENSORS[sensor][1]}"
                    else:
                        title = INVERTER_SENSORS[sensor][1]
                    sib = SunPowerInverterBasic(
                        coordinator,
                        data,
                        pvs,
                        INVERTER_SENSORS[sensor][0],
                        title,
                        INVERTER_SENSORS[sensor][2],
                        INVERTER_SENSORS[sensor][3],
                        INVERTER_SENSORS[sensor][4],
                        INVERTER_SENSORS[sensor][5]
                    )
                    try:
                        sib.native_value
                        entities.append(sib)
                    except KeyError:
                        pass

    async_add_entities(entities, True)


class SunPowerPVSBasic(SunPowerPVSEntity, SensorEntity):
    """Representation of SunPower PVS Stat"""

    def __init__(self, coordinator, pvs_info, field, title, unit, icon, device_class, state_class):
        """Initialize the sensor."""
        super().__init__(coordinator, pvs_info)
        self._title = title
        self._field = field
        self._unit = unit
        self._icon = icon
        self._my_device_class = device_class
        self._my_state_class = state_class

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def device_class(self):
        """Return device class."""
        return self._my_device_class

    @property
    def state_class(self):
        """Return state class."""
        return self._my_state_class

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
    def native_value(self):
        """Get the current value"""
        return self.coordinator.data[PVS_DEVICE_TYPE][self.base_unique_id][self._field]


class SunPowerMeterBasic(SunPowerMeterEntity, SensorEntity):
    """Representation of SunPower Meter Stat"""

    def __init__(self, coordinator, meter_info, pvs_info, field, title, unit, icon,
                 device_class, state_class):
        """Initialize the sensor."""
        super().__init__(coordinator, meter_info, pvs_info)
        self._title = title
        self._field = field
        self._unit = unit
        self._icon = icon
        self._my_device_class = device_class
        self._my_state_class = state_class

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def device_class(self):
        """Return device class."""
        return self._my_device_class

    @property
    def state_class(self):
        """Return state class."""
        return self._my_state_class

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
    def native_value(self):
        """Get the current value"""
        return self.coordinator.data[METER_DEVICE_TYPE][self.base_unique_id][self._field]


class SunPowerInverterBasic(SunPowerInverterEntity, SensorEntity):
    """Representation of SunPower Meter Stat"""

    def __init__(self, coordinator, inverter_info, pvs_info, field, title, unit, icon,
                 device_class, state_class):
        """Initialize the sensor."""
        super().__init__(coordinator, inverter_info, pvs_info)
        self._title = title
        self._field = field
        self._unit = unit
        self._icon = icon
        self._my_device_class = device_class
        self._my_state_class = state_class

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def device_class(self):
        """Return device class."""
        return self._my_device_class

    @property
    def state_class(self):
        """Return state class."""
        return self._my_state_class

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
    def native_value(self):
        """Get the current value"""
        return self.coordinator.data[INVERTER_DEVICE_TYPE][self.base_unique_id][self._field]
