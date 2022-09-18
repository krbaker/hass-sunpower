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
    SensorConfig,
)
from .entity import SunPowerPVSEntity, SunPowerMeterEntity, SunPowerInverterEntity


_LOGGER = logging.getLogger(__name__)


def validate_sensor(sensor: SensorEntity) -> bool:
    try:
        sensor.native_value
        return True
    except KeyError:
        return False


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
        return

    if INVERTER_DEVICE_TYPE not in sunpower_data:
        _LOGGER.error("Cannot find any power inverters")
    if METER_DEVICE_TYPE not in sunpower_data:
        _LOGGER.warn("Cannot find any power meters")

    pvs = next(iter(sunpower_data[PVS_DEVICE_TYPE].values()))

    entities = []
    entities += filter(
        validate_sensor,
        [
            SunPowerPVSBasic(
                coordinator,
                pvs,
                f"{pvs['DEVICE_TYPE']} " if do_descriptive_names else "",
                sensor_config,
            )
            for sensor_config in PVS_SENSORS.values()
        ],
    )

    for sensor_config in METER_SENSORS.values():
        entities += filter(
            validate_sensor,
            [
                SunPowerMeterBasic(
                    coordinator,
                    meter_data,
                    pvs,
                    f"{meter_data['DESCR']} " if do_descriptive_names else "",
                    sensor_config,
                )
                for meter_data in sunpower_data.get(METER_DEVICE_TYPE, {}).values()
            ],
        )

    for sensor_config in INVERTER_SENSORS.values():
        entities += filter(
            validate_sensor,
            [
                SunPowerInverterBasic(
                    coordinator,
                    inverter_data,
                    pvs,
                    f"{inverter_data['DESCR']} " if do_descriptive_names else "",
                    sensor_config,
                )
                for inverter_data in sunpower_data.get(INVERTER_DEVICE_TYPE, {}).values()
            ],
        )

    async_add_entities(entities, True)


class SunPowerPVSBasic(SunPowerPVSEntity, SensorEntity):
    """Representation of SunPower PVS Stat"""

    def __init__(self, coordinator, pvs_info, title_prefix, sensor_config):
        """Initialize the sensor."""
        super().__init__(coordinator, pvs_info)
        self._title_prefix = title_prefix
        self._config = sensor_config

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._config.unit

    @property
    def device_class(self):
        """Return device class."""
        return self._config.device_class

    @property
    def state_class(self):
        """Return state class."""
        return self._config.state_class

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._config.icon

    @property
    def name(self):
        """Device Name."""
        return f"{self._title_prefix}{self._config.title}"

    @property
    def unique_id(self):
        """Device Uniqueid."""
        return f"{self.base_unique_id}_pvs_{self._config.field}"

    @property
    def native_value(self):
        """Get the current value"""
        return self.coordinator.data[PVS_DEVICE_TYPE][self.base_unique_id][self._config.field]


class SunPowerMeterBasic(SunPowerMeterEntity, SensorEntity):
    """Representation of SunPower Meter Stat"""

    def __init__(self, coordinator, meter_info, pvs_info, title_prefix: str, sensor_config: SensorConfig):
        """Initialize the sensor."""
        super().__init__(coordinator, meter_info, pvs_info)
        self._title_prefix = title_prefix
        self._config = sensor_config

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._config.unit

    @property
    def device_class(self):
        """Return device class."""
        return self._config.device_class

    @property
    def state_class(self):
        """Return state class."""
        return self._config.state_class

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._config.icon

    @property
    def name(self):
        """Device Name."""
        return f"{self._title_prefix}{self._config.title}"

    @property
    def unique_id(self):
        """Device Uniqueid."""
        return f"{self.base_unique_id}_pvs_{self._config.field}"

    @property
    def native_value(self):
        """Get the current value"""
        return self.coordinator.data[METER_DEVICE_TYPE][self.base_unique_id][self._config.field]


class SunPowerInverterBasic(SunPowerInverterEntity, SensorEntity):
    """Representation of SunPower Meter Stat"""

    def __init__(self, coordinator, inverter_info, pvs_info, title_prefix: str, config: SensorConfig):
        """Initialize the sensor."""
        super().__init__(coordinator, inverter_info, pvs_info)
        self._title_prefix = title_prefix
        self._config = config

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._config.unit

    @property
    def device_class(self):
        """Return device class."""
        return self._config.device_class

    @property
    def state_class(self):
        """Return state class."""
        return self._config.state_class

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._config.icon

    @property
    def name(self):
        """Device Name."""
        return f"{self._title_prefix}{self._config.title}"

    @property
    def unique_id(self):
        """Device Uniqueid."""
        return f"{self.base_unique_id}_pvs_{self._config.field}"

    @property
    def native_value(self):
        """Get the current value"""
        return self.coordinator.data[INVERTER_DEVICE_TYPE][self.base_unique_id][self._config.field]
