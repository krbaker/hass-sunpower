"""Support for Sunpower sensors."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)

from .const import (
    DOMAIN,
    ESS_DEVICE_TYPE,
    PVS_DEVICE_TYPE,
    SUNPOWER_COORDINATOR,
    SUNPOWER_DESCRIPTIVE_NAMES,
    SUNPOWER_PRODUCT_NAMES,
    SUNPOWER_SENSORS,
    SUNVAULT_SENSORS,
)
from .entity import SunPowerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Sunpower sensors."""
    sunpower_state = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.debug("Sunpower_state: %s", sunpower_state)

    do_descriptive_names = False
    if SUNPOWER_DESCRIPTIVE_NAMES in config_entry.data:
        do_descriptive_names = config_entry.data[SUNPOWER_DESCRIPTIVE_NAMES]

    do_product_names = False
    if SUNPOWER_PRODUCT_NAMES in config_entry.data:
        do_product_names = config_entry.data[SUNPOWER_PRODUCT_NAMES]

    coordinator = sunpower_state[SUNPOWER_COORDINATOR]
    sunpower_data = coordinator.data

    do_ess = False
    if ESS_DEVICE_TYPE in sunpower_data:
        do_ess = True
    else:
        _LOGGER.debug("Found No ESS Data")

    if PVS_DEVICE_TYPE not in sunpower_data or not sunpower_data[PVS_DEVICE_TYPE]:
        _LOGGER.error("Cannot find PVS Entry or PVS data is empty")
    else:
        entities = []

        pvs = next(iter(sunpower_data[PVS_DEVICE_TYPE].values()))

        SENSORS = SUNPOWER_SENSORS
        if do_ess:
            SENSORS.update(SUNVAULT_SENSORS)

        for device_type in SENSORS:
            if device_type not in sunpower_data:
                _LOGGER.error(f"Cannot find any {device_type}")
                continue
            unique_id = SENSORS[device_type]["unique_id"]
            sensors = SENSORS[device_type]["sensors"]
            for index, sensor_data in enumerate(sunpower_data[device_type].values()):
                for sensor_name in sensors:
                    sensor = sensors[sensor_name]
                    sensor_type = (
                        "" if not do_descriptive_names else f"{sensor_data.get('TYPE', '')} "
                    )
                    sensor_description = (
                        "" if not do_descriptive_names else f"{sensor_data.get('DESCR', '')} "
                    )
                    text_sunpower = "" if not do_product_names else "SunPower "
                    text_sunvault = "" if not do_product_names else "SunVault "
                    text_pvs = "" if not do_product_names else "PVS "
                    sensor_index = "" if not do_descriptive_names else f"{index + 1} "
                    sunpower_sensor = SunPowerSensor(
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
                            SERIAL=sensor_data.get("SERIAL", "Unknown"),
                            MODEL=sensor_data.get("MODEL", "Unknown"),
                        ),
                        unit=sensor["unit"],
                        icon=sensor["icon"],
                        device_class=sensor["device"],
                        state_class=sensor["state"],
                        entity_category=sensor.get("entity_category", None),
                    )
                    if sunpower_sensor.native_value is not None:
                        entities.append(sunpower_sensor)

    async_add_entities(entities, True)


class SunPowerSensor(SunPowerEntity, SensorEntity):
    def __init__(
        self,
        coordinator,
        my_info,
        parent_info,
        id_code,
        device_type,
        field,
        title,
        unit,
        icon,
        device_class,
        state_class,
        entity_category,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator, my_info, parent_info)
        self._id_code = id_code
        self._device_type = device_type
        self._title = title
        self._field = field
        self._unit = unit
        self._icon = icon
        self._my_device_class = device_class
        self._my_state_class = state_class
        self._entity_category = entity_category

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def device_class(self):
        """Return device class."""
        return self._my_device_class

    @property
    def entity_category(self):
        return self._entity_category

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
        """Device Uniqueid.
        https://developers.home-assistant.io/docs/entity_registry_index/#unique-id
        Should not include the domain, home assistant does that for us
        base_unique_id is the serial number of the device (Inverter, PVS, Meter etc)
        "_pvs_" just as a divider - in case we start pulling data from some other source
        _field is the field within the data that this came from which is a dict so there
        is only one.
        Updating this format is a breaking change and should be called out if changed in a PR
        """
        return f"{self.base_unique_id}_pvs_{self._field}"

    @property
    def native_value(self):
        """Get the current value"""
        # Check if device type and device exist in coordinator data
        if (
            self._device_type not in self.coordinator.data
            or self.base_unique_id not in self.coordinator.data[self._device_type]
        ):
            return None
        
        if self._my_device_class == SensorDeviceClass.POWER_FACTOR:
            try:
                value = float(
                    self.coordinator.data[self._device_type][self.base_unique_id][self._field],
                )
                return value * 100.0
            except (ValueError, KeyError):
                pass  # sometimes this value might be something like 'unavailable'
        return self.coordinator.data[self._device_type][self.base_unique_id].get(self._field, None)
