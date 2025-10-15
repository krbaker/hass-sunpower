"""The sunpower integration."""

import logging
import time
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import (
    SOURCE_IMPORT,
    ConfigEntry,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    BATTERY_DEVICE_TYPE,
    DEFAULT_SUNPOWER_UPDATE_INTERVAL,
    DEFAULT_SUNVAULT_UPDATE_INTERVAL,
    DOMAIN,
    ESS_DEVICE_TYPE,
    HUBPLUS_DEVICE_TYPE,
    INVERTER_DEVICE_TYPE,
    METER_DEVICE_TYPE,
    PVS_DEVICE_TYPE,
    SETUP_TIMEOUT_MIN,
    SUNPOWER_COORDINATOR,
    SUNPOWER_HOST,
    SUNPOWER_OBJECT,
    SUNPOWER_UPDATE_INTERVAL,
    SUNVAULT_DEVICE_TYPE,
    SUNVAULT_UPDATE_INTERVAL,
)
from .sunpower import (
    ConnectionException,
    ParseException,
    SunPowerMonitor,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["sensor", "binary_sensor"]

PREVIOUS_PVS_SAMPLE_TIME = 0
PREVIOUS_PVS_SAMPLE = {}
PREVIOUS_ESS_SAMPLE_TIME = 0
PREVIOUS_ESS_SAMPLE = {}


def create_vmeter(data):
    # Create a virtual 'METER' that uses the sum of inverters
    kwh = 0.0
    kw = 0.0
    amps = 0.0
    freq = []
    volts = []
    state = "working"
    for _serial, inverter in data.get(INVERTER_DEVICE_TYPE, {}).items():
        if "STATE" in inverter and inverter["STATE"] != "working":
            state = inverter["STATE"]
        kwh += float(inverter.get("ltea_3phsum_kwh", "0"))
        kw += float(inverter.get("p_mppt1_kw", "0"))
        amps += float(inverter.get("i_3phsum_a", "0"))
        if "freq_hz" in inverter:
            freq.append(float(inverter["freq_hz"]))
        if "vln_3phavg_v" in inverter:
            volts.append(float(inverter["vln_3phavg_v"]))

    freq_avg = sum(freq) / len(freq) if len(freq) > 0 else None
    volts_avg = sum(volts) / len(volts) if len(volts) > 0 else None

    # Check if PVS device exists before trying to access it
    pvs_devices = data.get(PVS_DEVICE_TYPE)
    if not pvs_devices:
        _LOGGER.warning("PVS device not found in data, skipping virtual meter creation")
        return data
    
    pvs_serial = next(iter(pvs_devices))  # only one PVS
    vmeter_serial = f"{pvs_serial}pv"
    data.setdefault(METER_DEVICE_TYPE, {})[vmeter_serial] = {
        "SERIAL": vmeter_serial,
        "TYPE": "PVS-METER-P",
        "STATE": state,
        "MODEL": "Virtual",
        "DESCR": f"Power Meter {vmeter_serial}",
        "DEVICE_TYPE": "Power Meter",
        "interface": "virtual",
        "SWVER": "1.0",
        "HWVER": "Virtual",
        "origin": "virtual",
        "net_ltea_3phsum_kwh": kwh,
        "p_3phsum_kw": kw,
        "freq_hz": freq_avg,
        "i_a": amps,
        "v12_v": volts_avg,
    }
    return data


def convert_sunpower_data(sunpower_data):
    """Convert PVS data into indexable format data[device_type][serial]"""
    data = {}
    
    # Log total device count
    total_devices = len(sunpower_data.get("devices", []))
    _LOGGER.info(f"Processing {total_devices} devices from API")
    
    for device in sunpower_data["devices"]:
        device_type = device.get("DEVICE_TYPE", "UNKNOWN")
        serial = device.get("SERIAL", "UNKNOWN")
        data.setdefault(device_type, {})[serial] = device

    # Log device types found for debugging
    device_types = list(data.keys())
    device_counts = {dt: len(data[dt]) for dt in device_types}
    _LOGGER.info(f"Device types found: {device_counts}")
    
    # Check for expected device types
    if not data.get(PVS_DEVICE_TYPE):
        _LOGGER.error(f"CRITICAL: PVS device type '{PVS_DEVICE_TYPE}' not found!")
        _LOGGER.error(f"Available device types: {device_types}")
        # Log ALL devices to see what we're getting
        for i, dev in enumerate(sunpower_data["devices"][:10]):  # First 10 devices
            _LOGGER.error(f"Device {i+1}: TYPE='{dev.get('DEVICE_TYPE')}', SERIAL={dev.get('SERIAL')}, MODEL={dev.get('MODEL')}")
    
    if not data.get(INVERTER_DEVICE_TYPE):
        _LOGGER.warning(f"No inverter devices found - this is normal for some PVS configurations")
        _LOGGER.info(f"Available device types: {device_types}")
        _LOGGER.info("Inverter data may be aggregated in meter readings or unavailable via LocalAPI")

    create_vmeter(data)

    return data


def convert_ess_data(ess_data, data):
    """Do all the gymnastics to Integrate ESS data from its unique data source into the PVS data"""
    sunvault_amperages = []
    sunvault_voltages = []
    sunvault_temperatures = []
    sunvault_customer_state_of_charges = []
    sunvault_system_state_of_charges = []
    sunvault_power = []
    sunvault_power_inputs = []
    sunvault_power_outputs = []
    sunvault_state = "working"
    
    # Ensure device types exist in data
    if BATTERY_DEVICE_TYPE not in data:
        _LOGGER.warning("BATTERY_DEVICE_TYPE not found in data, skipping battery ESS data conversion")
        data[BATTERY_DEVICE_TYPE] = {}
    if ESS_DEVICE_TYPE not in data:
        _LOGGER.warning("ESS_DEVICE_TYPE not found in data, skipping ESS data conversion")
        data[ESS_DEVICE_TYPE] = {}
    if HUBPLUS_DEVICE_TYPE not in data:
        _LOGGER.warning("HUBPLUS_DEVICE_TYPE not found in data, skipping HubPlus data conversion")
        data[HUBPLUS_DEVICE_TYPE] = {}
    
    for device in ess_data["ess_report"]["battery_status"]:
        serial = device["serial_number"]
        if serial not in data[BATTERY_DEVICE_TYPE]:
            _LOGGER.warning(f"Battery {serial} not found in PVS data, skipping")
            continue
        data[BATTERY_DEVICE_TYPE][serial]["battery_amperage"] = device[
            "battery_amperage"
        ]["value"]
        data[BATTERY_DEVICE_TYPE][serial]["battery_voltage"] = device[
            "battery_voltage"
        ]["value"]
        data[BATTERY_DEVICE_TYPE][serial]["customer_state_of_charge"] = device[
            "customer_state_of_charge"
        ]["value"]
        data[BATTERY_DEVICE_TYPE][serial]["system_state_of_charge"] = device[
            "system_state_of_charge"
        ]["value"]
        data[BATTERY_DEVICE_TYPE][serial]["temperature"] = device["temperature"][
            "value"
        ]
        if data[BATTERY_DEVICE_TYPE][serial]["STATE"] != "working":
            sunvault_state = data[BATTERY_DEVICE_TYPE][serial]["STATE"]
        sunvault_amperages.append(device["battery_amperage"]["value"])
        sunvault_voltages.append(device["battery_voltage"]["value"])
        sunvault_temperatures.append(device["temperature"]["value"])
        sunvault_customer_state_of_charges.append(
            device["customer_state_of_charge"]["value"],
        )
        sunvault_system_state_of_charges.append(device["system_state_of_charge"]["value"])
        sunvault_power.append(sunvault_amperages[-1] * sunvault_voltages[-1])
        if sunvault_amperages[-1] < 0:
            sunvault_power_outputs.append(
                abs(sunvault_amperages[-1] * sunvault_voltages[-1]),
            )
            sunvault_power_inputs.append(0)
        elif sunvault_amperages[-1] > 0:
            sunvault_power_inputs.append(sunvault_amperages[-1] * sunvault_voltages[-1])
            sunvault_power_outputs.append(0)
        else:
            sunvault_power_inputs.append(0)
            sunvault_power_outputs.append(0)
    for device in ess_data["ess_report"]["ess_status"]:
        serial = device["serial_number"]
        if serial not in data[ESS_DEVICE_TYPE]:
            _LOGGER.warning(f"ESS {serial} not found in PVS data, skipping")
            continue
        data[ESS_DEVICE_TYPE][serial]["enclosure_humidity"] = device[
            "enclosure_humidity"
        ]["value"]
        data[ESS_DEVICE_TYPE][serial]["enclosure_temperature"] = device[
            "enclosure_temperature"
        ]["value"]
        data[ESS_DEVICE_TYPE][serial]["agg_power"] = device["ess_meter_reading"][
            "agg_power"
        ]["value"]
        data[ESS_DEVICE_TYPE][serial]["meter_a_current"] = device[
            "ess_meter_reading"
        ]["meter_a"]["reading"]["current"]["value"]
        data[ESS_DEVICE_TYPE][serial]["meter_a_power"] = device[
            "ess_meter_reading"
        ]["meter_a"]["reading"]["power"]["value"]
        data[ESS_DEVICE_TYPE][serial]["meter_a_voltage"] = device[
            "ess_meter_reading"
        ]["meter_a"]["reading"]["voltage"]["value"]
        data[ESS_DEVICE_TYPE][serial]["meter_b_current"] = device[
            "ess_meter_reading"
        ]["meter_b"]["reading"]["current"]["value"]
        data[ESS_DEVICE_TYPE][serial]["meter_b_power"] = device[
            "ess_meter_reading"
        ]["meter_b"]["reading"]["power"]["value"]
        data[ESS_DEVICE_TYPE][serial]["meter_b_voltage"] = device[
            "ess_meter_reading"
        ]["meter_b"]["reading"]["voltage"]["value"]
    if True:
        device = ess_data["ess_report"]["hub_plus_status"]
        serial = device["serial_number"]
        if serial not in data[HUBPLUS_DEVICE_TYPE]:
            _LOGGER.warning(f"HubPlus {serial} not found in PVS data, skipping")
        else:
            data[HUBPLUS_DEVICE_TYPE][serial]["contactor_position"] = device[
                "contactor_position"
            ]
            data[HUBPLUS_DEVICE_TYPE][serial]["grid_frequency_state"] = device[
                "grid_frequency_state"
            ]
            data[HUBPLUS_DEVICE_TYPE][serial]["grid_phase1_voltage"] = device[
                "grid_phase1_voltage"
            ]["value"]
            data[HUBPLUS_DEVICE_TYPE][serial]["grid_phase2_voltage"] = device[
                "grid_phase2_voltage"
            ]["value"]
            data[HUBPLUS_DEVICE_TYPE][serial]["grid_voltage_state"] = device[
                "grid_voltage_state"
            ]
            data[HUBPLUS_DEVICE_TYPE][serial]["hub_humidity"] = device[
                "hub_humidity"
            ]["value"]
            data[HUBPLUS_DEVICE_TYPE][serial]["hub_temperature"] = device[
                "hub_temperature"
            ]["value"]
            data[HUBPLUS_DEVICE_TYPE][serial]["inverter_connection_voltage"] = device[
                "inverter_connection_voltage"
            ]["value"]
            data[HUBPLUS_DEVICE_TYPE][serial]["load_frequency_state"] = device[
                "load_frequency_state"
            ]
            data[HUBPLUS_DEVICE_TYPE][serial]["load_phase1_voltage"] = device[
                "load_phase1_voltage"
            ]["value"]
            data[HUBPLUS_DEVICE_TYPE][serial]["load_phase2_voltage"] = device[
                "load_phase2_voltage"
            ]["value"]
            data[HUBPLUS_DEVICE_TYPE][serial]["main_voltage"] = device[
                "main_voltage"
            ]["value"]
    if True:
        # Generate a usable serial number for this virtual device, use PVS serial as base
        # since we must be talking through one and it has a serial
        # Check if PVS device exists before trying to access it
        pvs_devices = data.get(PVS_DEVICE_TYPE)
        if not pvs_devices:
            _LOGGER.warning("PVS device not found in data, skipping SunVault virtual device creation")
            return data
        
        pvs_serial = next(iter(pvs_devices))  # only one PVS
        sunvault_serial = f"sunvault_{pvs_serial}"
        data[SUNVAULT_DEVICE_TYPE] = {sunvault_serial: {}}
        data[SUNVAULT_DEVICE_TYPE][sunvault_serial]["sunvault_amperage"] = sum(
            sunvault_amperages,
        )
        data[SUNVAULT_DEVICE_TYPE][sunvault_serial]["sunvault_voltage"] = sum(
            sunvault_voltages,
        ) / len(sunvault_voltages)
        data[SUNVAULT_DEVICE_TYPE][sunvault_serial]["sunvault_temperature"] = sum(
            sunvault_temperatures,
        ) / len(sunvault_temperatures)
        data[SUNVAULT_DEVICE_TYPE][sunvault_serial]["sunvault_customer_state_of_charge"] = sum(
            sunvault_customer_state_of_charges,
        ) / len(sunvault_customer_state_of_charges)
        data[SUNVAULT_DEVICE_TYPE][sunvault_serial]["sunvault_system_state_of_charge"] = sum(
            sunvault_system_state_of_charges,
        ) / len(sunvault_system_state_of_charges)
        data[SUNVAULT_DEVICE_TYPE][sunvault_serial]["sunvault_power_input"] = sum(
            sunvault_power_inputs,
        )
        data[SUNVAULT_DEVICE_TYPE][sunvault_serial]["sunvault_power_output"] = sum(
            sunvault_power_outputs,
        )
        data[SUNVAULT_DEVICE_TYPE][sunvault_serial]["sunvault_power"] = sum(sunvault_power)
        data[SUNVAULT_DEVICE_TYPE][sunvault_serial]["STATE"] = sunvault_state
        data[SUNVAULT_DEVICE_TYPE][sunvault_serial]["SERIAL"] = sunvault_serial
        data[SUNVAULT_DEVICE_TYPE][sunvault_serial]["SWVER"] = "1.0"
        data[SUNVAULT_DEVICE_TYPE][sunvault_serial]["HWVER"] = "Virtual"
        data[SUNVAULT_DEVICE_TYPE][sunvault_serial]["DESCR"] = "Virtual SunVault"
        data[SUNVAULT_DEVICE_TYPE][sunvault_serial]["MODEL"] = "Virtual SunVault"
    return data


def sunpower_fetch(
    sunpower_monitor,
    sunpower_update_invertal,
    sunvault_update_invertal,
):
    """Basic data fetch routine to get and reformat sunpower data to a dict of device
    type and serial #"""
    global PREVIOUS_PVS_SAMPLE_TIME
    global PREVIOUS_PVS_SAMPLE
    global PREVIOUS_ESS_SAMPLE_TIME
    global PREVIOUS_ESS_SAMPLE

    sunpower_data = PREVIOUS_PVS_SAMPLE
    ess_data = PREVIOUS_ESS_SAMPLE
    use_ess = False
    data = None

    try:
        if (time.time() - PREVIOUS_PVS_SAMPLE_TIME) >= (sunpower_update_invertal - 1):
            PREVIOUS_PVS_SAMPLE_TIME = time.time()
            sunpower_data = sunpower_monitor.device_list()
            PREVIOUS_PVS_SAMPLE = sunpower_data
            _LOGGER.debug("got PVS data %s", sunpower_data)
    except (ParseException, ConnectionException) as error:
        raise UpdateFailed from error

    if not sunpower_data or "devices" not in sunpower_data:
        _LOGGER.error("Invalid PVS data structure: %s", sunpower_data)
        raise UpdateFailed("PVS returned invalid data structure - missing 'devices' key")

    data = convert_sunpower_data(sunpower_data)
    if ESS_DEVICE_TYPE in data:  # Look for an ESS in PVS data
        use_ess = True

    try:
        if use_ess and (time.time() - PREVIOUS_ESS_SAMPLE_TIME) >= (sunvault_update_invertal - 1):
            PREVIOUS_ESS_SAMPLE_TIME = time.time()
            ess_data = sunpower_monitor.energy_storage_system_status()
            PREVIOUS_ESS_SAMPLE = ess_data
            _LOGGER.debug("got ESS data %s", ess_data)
    except (ParseException, ConnectionException) as error:
        raise UpdateFailed from error

    try:
        if use_ess:
            convert_ess_data(
                ess_data,
                data,
            )  # ess converter appends to items in existing PVS structure
        return data
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
        ),
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up sunpower from a config entry."""
    _LOGGER.debug(f"Setting up {entry.entry_id}, Options {entry.options}, Config {entry.data}")
    entry_id = entry.entry_id

    hass.data[DOMAIN].setdefault(entry_id, {})
    # Create monitor in executor since __init__ makes blocking calls
    sunpower_monitor = await hass.async_add_executor_job(
        SunPowerMonitor,
        entry.data[SUNPOWER_HOST],
        None,  # Auto-fetch from PVS
    )
    sunpower_update_invertal = entry.options.get(
        SUNPOWER_UPDATE_INTERVAL,
        DEFAULT_SUNPOWER_UPDATE_INTERVAL,
    )
    sunvault_update_invertal = entry.options.get(
        SUNVAULT_UPDATE_INTERVAL,
        DEFAULT_SUNVAULT_UPDATE_INTERVAL,
    )

    async def async_update_data():
        """Fetch data from API endpoint, used by coordinator to get mass data updates"""
        _LOGGER.debug("Updating SunPower data")
        return await hass.async_add_executor_job(
            sunpower_fetch,
            sunpower_monitor,
            sunpower_update_invertal,
            sunvault_update_invertal,
        )

    # This could be better, taking the shortest time interval as the coordinator update is fine
    # if the long interval is an even multiple of the short or *much* smaller
    coordinator_interval = (
        sunvault_update_invertal
        if sunvault_update_invertal < sunpower_update_invertal
        else sunpower_update_invertal
    )

    _LOGGER.debug(
        f"Intervals: Sunpower {sunpower_update_invertal} Sunvault {sunvault_update_invertal}",
    )
    _LOGGER.debug(f"Coordinator update interval set to {coordinator_interval}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="SunPower PVS",
        update_method=async_update_data,
        update_interval=timedelta(seconds=coordinator_interval),
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

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    _LOGGER.debug(
        "Updating: %s with data=%s and options=%s",
        entry.entry_id,
        entry.data,
        entry.options,
    )
    _LOGGER.debug("Update listener called, reloading")
    await hass.config_entries.async_reload(entry.entry_id)
    _LOGGER.debug("Update listener done reloading")


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
