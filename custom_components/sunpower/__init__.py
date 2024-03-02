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
    SUNPOWER_ESS,
    SETUP_TIMEOUT_MIN,
    BATTERY_DEVICE_TYPE,
    ESS_DEVICE_TYPE,
    HUBPLUS_DEVICE_TYPE,
    SUNVAULT_DEVICE_TYPE
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["sensor", "binary_sensor"]


def sunpower_fetch(sunpower_monitor, use_ess):
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

        if use_ess:
            # Integrate ESS data from its unique data source into the PVS data
            sunpower_data = sunpower_monitor.energy_storage_system_status()
            _LOGGER.debug("got data %s", sunpower_data)
            sunvault_amperages = []
            sunvault_voltages = []
            sunvault_temperatures = []
            sunvault_customer_state_of_charges = []
            sunvault_system_state_of_charges = []
            sunvault_power = []
            sunvault_power_inputs = []
            sunvault_power_outputs = []
            sunvault_state = "working"
            for device in sunpower_data["ess_report"]["battery_status"]:
                data[BATTERY_DEVICE_TYPE][device["serial_number"]]["battery_amperage"] = device["battery_amperage"]["value"]
                data[BATTERY_DEVICE_TYPE][device["serial_number"]]["battery_voltage"] = device["battery_voltage"]["value"]
                data[BATTERY_DEVICE_TYPE][device["serial_number"]]["customer_state_of_charge"] = device["customer_state_of_charge"]["value"]
                data[BATTERY_DEVICE_TYPE][device["serial_number"]]["system_state_of_charge"] = device["system_state_of_charge"]["value"]
                data[BATTERY_DEVICE_TYPE][device["serial_number"]]["temperature"] = device["temperature"]["value"]
                if data[BATTERY_DEVICE_TYPE][device["serial_number"]]["STATE"] != "working":
                    sunvault_state = data[BATTERY_DEVICE_TYPE][device["serial_number"]]["STATE"]
                sunvault_amperages.append(device["battery_amperage"]["value"])
                sunvault_voltages.append(device["battery_voltage"]["value"])
                sunvault_temperatures.append(device["temperature"]["value"])
                sunvault_customer_state_of_charges.append(device["customer_state_of_charge"]["value"])
                sunvault_system_state_of_charges.append(device["system_state_of_charge"]["value"])
                sunvault_power.append(sunvault_amperages[-1] * sunvault_voltages[-1])
                if sunvault_amperages[-1] < 0:
                    sunvault_power_outputs.append(abs(sunvault_amperages[-1] * sunvault_voltages[-1]))
                    sunvault_power_inputs.append(0)
                elif sunvault_amperages[-1] > 0:
                    sunvault_power_inputs.append(sunvault_amperages[-1] * sunvault_voltages[-1])
                    sunvault_power_outputs.append(0)
                else:
                    sunvault_power_inputs.append(0)
                    sunvault_power_outputs.append(0)
            for device in sunpower_data["ess_report"]["ess_status"]:
                data[ESS_DEVICE_TYPE][device["serial_number"]]["enclosure_humidity"] = device["enclosure_humidity"]["value"]
                data[ESS_DEVICE_TYPE][device["serial_number"]]["enclosure_temperature"] = device["enclosure_temperature"]["value"]
                data[ESS_DEVICE_TYPE][device["serial_number"]]["agg_power"] = device["ess_meter_reading"]["agg_power"]["value"]
                data[ESS_DEVICE_TYPE][device["serial_number"]]["meter_a_current"] = device["ess_meter_reading"]["meter_a"]["reading"]["current"]["value"]
                data[ESS_DEVICE_TYPE][device["serial_number"]]["meter_a_power"] = device["ess_meter_reading"]["meter_a"]["reading"]["power"]["value"]
                data[ESS_DEVICE_TYPE][device["serial_number"]]["meter_a_voltage"] = device["ess_meter_reading"]["meter_a"]["reading"]["voltage"]["value"]
                data[ESS_DEVICE_TYPE][device["serial_number"]]["meter_b_current"] = device["ess_meter_reading"]["meter_b"]["reading"]["current"]["value"]
                data[ESS_DEVICE_TYPE][device["serial_number"]]["meter_b_power"] = device["ess_meter_reading"]["meter_b"]["reading"]["power"]["value"]
                data[ESS_DEVICE_TYPE][device["serial_number"]]["meter_b_voltage"] = device["ess_meter_reading"]["meter_b"]["reading"]["voltage"]["value"]
            if True:
                device = sunpower_data["ess_report"]["hub_plus_status"]
                data[HUBPLUS_DEVICE_TYPE][device["serial_number"]]["contactor_position"] = device["contactor_position"]
                data[HUBPLUS_DEVICE_TYPE][device["serial_number"]]["grid_frequency_state"] = device["grid_frequency_state"]
                data[HUBPLUS_DEVICE_TYPE][device["serial_number"]]["grid_phase1_voltage"] = device["grid_phase1_voltage"]["value"]
                data[HUBPLUS_DEVICE_TYPE][device["serial_number"]]["grid_phase2_voltage"] = device["grid_phase2_voltage"]["value"]
                data[HUBPLUS_DEVICE_TYPE][device["serial_number"]]["grid_voltage_state"] = device["grid_voltage_state"]
                data[HUBPLUS_DEVICE_TYPE][device["serial_number"]]["hub_humidity"] = device["hub_humidity"]["value"]
                data[HUBPLUS_DEVICE_TYPE][device["serial_number"]]["hub_temperature"] = device["hub_temperature"]["value"]
                data[HUBPLUS_DEVICE_TYPE][device["serial_number"]]["inverter_connection_voltage"] = device["inverter_connection_voltage"]["value"]
                data[HUBPLUS_DEVICE_TYPE][device["serial_number"]]["load_frequency_state"] = device["load_frequency_state"]
                data[HUBPLUS_DEVICE_TYPE][device["serial_number"]]["load_phase1_voltage"] = device["load_phase1_voltage"]["value"]
                data[HUBPLUS_DEVICE_TYPE][device["serial_number"]]["load_phase2_voltage"] = device["load_phase2_voltage"]["value"]
                data[HUBPLUS_DEVICE_TYPE][device["serial_number"]]["main_voltage"] = device["main_voltage"]["value"]
            if True:
                data[SUNVAULT_DEVICE_TYPE] = { "SunVault" : { } }
                data[SUNVAULT_DEVICE_TYPE]["SunVault"]["sunvault_amperage"] = sum(sunvault_amperages)
                data[SUNVAULT_DEVICE_TYPE]["SunVault"]["sunvault_voltage"] = sum(sunvault_voltages) / len(sunvault_voltages)
                data[SUNVAULT_DEVICE_TYPE]["SunVault"]["sunvault_temperature"] = sum(sunvault_temperatures) / len(sunvault_temperatures)
                data[SUNVAULT_DEVICE_TYPE]["SunVault"]["sunvault_customer_state_of_charge"] = sum(sunvault_customer_state_of_charges) / len(sunvault_customer_state_of_charges)
                data[SUNVAULT_DEVICE_TYPE]["SunVault"]["sunvault_system_state_of_charge"] = sum(sunvault_system_state_of_charges) / len(sunvault_system_state_of_charges)
                data[SUNVAULT_DEVICE_TYPE]["SunVault"]["sunvault_power_input"] = sum(sunvault_power_inputs)
                data[SUNVAULT_DEVICE_TYPE]["SunVault"]["sunvault_power_output"] = sum(sunvault_power_outputs)
                data[SUNVAULT_DEVICE_TYPE]["SunVault"]["sunvault_power"] = sum(sunvault_power)
                data[SUNVAULT_DEVICE_TYPE]["SunVault"]["STATE"] = sunvault_state
                data[SUNVAULT_DEVICE_TYPE]["SunVault"]["SERIAL"] = "SunVault"
                data[SUNVAULT_DEVICE_TYPE]["SunVault"]["SWVER"] = "1.0"
                data[SUNVAULT_DEVICE_TYPE]["SunVault"]["DESCR"] = "SunVault"
                data[SUNVAULT_DEVICE_TYPE]["SunVault"]["MODEL"] = "SunVault"
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
    use_ess = entry.data[SUNPOWER_ESS]

    async def async_update_data():
        """Fetch data from API endpoint, used by coordinator to get mass data updates"""
        _LOGGER.debug("Updating SunPower data")
        return await hass.async_add_executor_job(sunpower_fetch, sunpower_monitor, use_ess)

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
