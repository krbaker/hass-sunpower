"""The sunpower integration."""
import asyncio
from datetime import timedelta
import logging
import time

import voluptuous as vol

from .sunpower import SunPowerMonitor, ConnectionException, ParseException

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    UPDATE_INTERVAL,
    SUNPOWER_OBJECT,
    SUNPOWER_COORDINATOR,
    SUNPOWER_HOST,
    SETUP_TIMEOUT_MIN,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["sensor", "binary_sensor"]


def sunpower_fetch(sunpower_monitor):
    """Basic data fetch routine to get and reformat sunpower data to a dict of device type and serial #"""
    try:
        sunpower_data = sunpower_monitor.device_list()
        _LOGGER.debug("got data %s", sunpower_data)
        data = {}
        # Convert data into indexable format data[device_type][serial]
        for device in sunpower_data["devices"]:
            if device["DEVICE_TYPE"] not in data:
                data[device["DEVICE_TYPE"]] = {device["SERIAL"]: device}
            else:
                data[device["DEVICE_TYPE"]][device["SERIAL"]] = device
        return data
    except ConnectionException as error:
        raise UpdateFailed from error
    except ParseException as error:
        raise UpdateFailed from error


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the sunpower component."""
    hass.data.setdefault(DOMAIN, {})
    conf = config.get(DOMAIN)

    if not conf:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data=conf,
        )
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up sunpower from a config entry."""
    entry_id = entry.entry_id

    hass.data[DOMAIN].setdefault(entry_id, {})
    sunpower_monitor = SunPowerMonitor(entry.data[SUNPOWER_HOST])

    async def async_update_data():
        """Fetch data from API endpoint, used by coordinator to get mass data updates"""
        _LOGGER.debug("Updating SunPower data")
        return await hass.async_add_executor_job(sunpower_fetch, sunpower_monitor)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="SunPower PVS",
        update_method=async_update_data,
        update_interval=timedelta(seconds=UPDATE_INTERVAL),
    )

    hass.data[DOMAIN][entry.entry_id] = {
        SUNPOWER_OBJECT: sunpower_monitor,
        SUNPOWER_COORDINATOR: coordinator,
    }

    start = time.time()
    # Need to make sure this data loads on setup, be aggressive about retries
    while not coordinator.data:
        _LOGGER.debug("Config Update Attempt")
        await coordinator.async_refresh()
        if (time.time() - start) > (SETUP_TIMEOUT_MIN * 60):
            _LOGGER.error("Failed to update data")
            break

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
