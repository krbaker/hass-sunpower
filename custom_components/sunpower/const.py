"""Constants for the sunpower integration."""
from collections import namedtuple

from homeassistant.const import (
    TIME_SECONDS,
    DATA_KILOBYTES,
    FREQUENCY_HERTZ,
    ENERGY_KILO_WATT_HOUR,
    POWER_KILO_WATT,
    POWER_VOLT_AMPERE,
    PERCENTAGE,
    ELECTRIC_POTENTIAL_VOLT,
    ELECTRIC_CURRENT_AMPERE,
    TEMP_CELSIUS,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_VOLTAGE,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_POWER_FACTOR,
)

from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL,
    STATE_CLASS_TOTAL_INCREASING,
)

DOMAIN = "sunpower"

SUNPOWER_DESCRIPTIVE_NAMES = "use_descriptive_names"
SUNPOWER_OBJECT = "sunpower"
SUNPOWER_HOST = "host"
SUNPOWER_COORDINATOR = "coordinator"
UPDATE_INTERVAL = 120
SETUP_TIMEOUT_MIN = 5

PVS_DEVICE_TYPE = "PVS"
INVERTER_DEVICE_TYPE = "Inverter"
METER_DEVICE_TYPE = "Power Meter"

PVS_STATE = "STATE"

METER_STATE = "STATE"

INVERTER_STATE = "STATE"

WORKING_STATE = "working"


sensor_config = namedtuple("sensor_config", "field title unit icon device_class state_class")

METER_SENSORS = {
    "METER_FREQUENCY": sensor_config(
        "freq_hz", "Frequency", FREQUENCY_HERTZ, "mdi:flash", None, STATE_CLASS_MEASUREMENT
    ),
    "METER_NET_KWH": sensor_config(
        "net_ltea_3phsum_kwh",
        "Lifetime Power",
        ENERGY_KILO_WATT_HOUR,
        "mdi:flash",
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
    ),
    "METER_KW": sensor_config(
        "p_3phsum_kw", "Power", POWER_KILO_WATT, "mdi:flash", DEVICE_CLASS_POWER, STATE_CLASS_MEASUREMENT
    ),
    "METER_VAR": sensor_config(
        "q_3phsum_kvar", "KVA Reactive", POWER_VOLT_AMPERE, "mdi:flash", None, STATE_CLASS_MEASUREMENT
    ),
    "METER_VA": sensor_config(
        "s_3phsum_kva", "KVA Apparent", POWER_VOLT_AMPERE, "mdi:flash", None, STATE_CLASS_MEASUREMENT
    ),
    "METER_POWER_FACTOR": sensor_config(
        "tot_pf_rto", "Power Factor", PERCENTAGE, "mdi:flash", DEVICE_CLASS_POWER_FACTOR, STATE_CLASS_MEASUREMENT
    ),
    "METER_L1_A": sensor_config(
        "i1_a", "Leg 1 Amps", ELECTRIC_CURRENT_AMPERE, "mdi:flash", DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT
    ),
    "METER_L2_A": sensor_config(
        "i2_a", "Leg 2 Amps", ELECTRIC_CURRENT_AMPERE, "mdi:flash", DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT
    ),
    "METER_L1_KW": sensor_config(
        "p1_kw", "Leg 1 KW", POWER_KILO_WATT, "mdi:flash", DEVICE_CLASS_POWER, STATE_CLASS_MEASUREMENT
    ),
    "METER_L2_KW": sensor_config(
        "p2_kw", "Leg 2 KW", POWER_KILO_WATT, "mdi:flash", DEVICE_CLASS_POWER, STATE_CLASS_MEASUREMENT
    ),
    "METER_L1_V": sensor_config(
        "v1n_v", "Leg 1 Volts", ELECTRIC_POTENTIAL_VOLT, "mdi:flash", DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT
    ),
    "METER_L2_V": sensor_config(
        "v2n_v", "Leg 2 Volts", ELECTRIC_POTENTIAL_VOLT, "mdi:flash", DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT
    ),
    "METER_L12_V": sensor_config(
        "v12_v", "Supply Volts", ELECTRIC_POTENTIAL_VOLT, "mdi:flash", DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT
    ),
    "METER_TO_GRID": sensor_config(
        "neg_ltea_3phsum_kwh",
        "KWH To Grid",
        ENERGY_KILO_WATT_HOUR,
        "mdi:flash",
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
    ),
    "METER_TO_HOME": sensor_config(
        "pos_ltea_3phsum_kwh",
        "KWH To Home",
        ENERGY_KILO_WATT_HOUR,
        "mdi:flash",
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
    ),
}

INVERTER_SENSORS = {
    "INVERTER_NET_KWH": sensor_config(
        "ltea_3phsum_kwh",
        "Lifetime Power",
        ENERGY_KILO_WATT_HOUR,
        "mdi:flash",
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
    ),
    "INVERTER_KW": sensor_config(
        "p_3phsum_kw", "Power", POWER_KILO_WATT, "mdi:flash", DEVICE_CLASS_POWER, STATE_CLASS_MEASUREMENT
    ),
    "INVERTER_VOLTS": sensor_config(
        "vln_3phavg_v", "Voltage", ELECTRIC_POTENTIAL_VOLT, "mdi:flash", DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT
    ),
    "INVERTER_AMPS": sensor_config(
        "i_3phsum_a", "Amps", ELECTRIC_CURRENT_AMPERE, "mdi:flash", DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT
    ),
    "INVERTER_MPPT_KW": sensor_config(
        "p_mpptsum_kw", "MPPT KW", POWER_KILO_WATT, "mdi:flash", DEVICE_CLASS_POWER, STATE_CLASS_MEASUREMENT
    ),
    "INVERTER_MPPT1_KW": sensor_config(
        "p_mppt1_kw", "MPPT KW", POWER_KILO_WATT, "mdi:flash", DEVICE_CLASS_POWER, STATE_CLASS_MEASUREMENT
    ),
    "INVERTER_MPPT_V": sensor_config(
        "v_mppt1_v", "MPPT Volts", ELECTRIC_POTENTIAL_VOLT, "mdi:flash", DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT
    ),
    "INVERTER_MPPT_A": sensor_config(
        "i_mppt1_a", "MPPT Amps", POWER_VOLT_AMPERE, "mdi:flash", DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT
    ),
    "INVERTER_TEMPERATURE": sensor_config(
        "t_htsnk_degc",
        "Temperature",
        TEMP_CELSIUS,
        "mdi:thermometer",
        DEVICE_CLASS_TEMPERATURE,
        STATE_CLASS_MEASUREMENT,
    ),
    "INVERTER_FREQUENCY": sensor_config(
        "freq_hz", "Frequency", FREQUENCY_HERTZ, "mdi:flash", None, STATE_CLASS_MEASUREMENT
    ),
}


PVS_SENSORS = {
    "PVS_LOAD": sensor_config("dl_cpu_load", "System Load", "", "mdi:gauge", None, STATE_CLASS_MEASUREMENT),
    "PVS_ERROR_COUNT": sensor_config("dl_err_count", "Error Count", "", "mdi:alert-circle", None, STATE_CLASS_TOTAL),
    "PVS_COMMUNICATION_ERRORS": sensor_config(
        "dl_comm_err", "Communication Errors", "", "mdi:network-off", None, STATE_CLASS_TOTAL
    ),
    "PVS_SKIPPED_SCANS": sensor_config(
        "dl_skipped_scans", "Skipped Scans", "", "mdi:network-strength-off-outline", None, STATE_CLASS_TOTAL_INCREASING
    ),
    "PVS_SCAN_TIME": sensor_config(
        "dl_scan_time", "Scan Time", TIME_SECONDS, "mdi:timer-outline", None, STATE_CLASS_MEASUREMENT
    ),
    "PVS_UNTRANSMITTED": sensor_config(
        "dl_untransmitted", "Untransmitted Data", "", "mdi:radio-tower", None, STATE_CLASS_MEASUREMENT
    ),
    "PVS_UPTIME": sensor_config(
        "dl_uptime", "Uptime", TIME_SECONDS, "mdi:timer-outline", None, STATE_CLASS_TOTAL_INCREASING
    ),
    "PVS_MEMORY_USED": sensor_config(
        "dl_mem_used", "Memory Used", DATA_KILOBYTES, "mdi:memory", None, STATE_CLASS_MEASUREMENT
    ),
    "PVS_FLASH_AVAILABLE": sensor_config(
        "dl_flash_avail", "Flash Available", DATA_KILOBYTES, "mdi:memory", None, STATE_CLASS_MEASUREMENT
    ),
}

SENSOR_CONFIGS = {
    PVS_DEVICE_TYPE: PVS_SENSORS,
    INVERTER_DEVICE_TYPE: INVERTER_SENSORS,
    METER_DEVICE_TYPE: METER_SENSORS,
}

FIELD_ADAPTORS = {
    PVS_DEVICE_TYPE: {
        "dl_cpu_load": {"Avg CPU Load": "2.2.3"},
        "dl_err_count": {"Error Count": "2.2.3"},
        "dl_comm_err": {"Communication Error Count": "2.2.3"},
        "dl_skipped_scans": {"Skipped Scans": "2.2.3"},
        "dl_scan_time": {"Scan Time": "2.2.3"},
        "dl_untransmitted": {"Untransmitted Data Points": "2.2.3"},
        "dl_uptime": {"Time Since Powerup": "2.2.3"},
        "dl_mem_used": {"Memory Used": "2.2.3"},
        "dl_flash_avail": {"Flash Space Available": "2.2.3"},
        "SERIAL": {"Serial Number": "2.2.3"},
    },
    INVERTER_DEVICE_TYPE: {
        "ltea_3phsum_kwh": {"Total Lifetime Energy": "2.2.3"},
        "p_3phsum_kw": {"Avg DC Power": "2.2.3"},
        "vln_3phavg_v": {"Avg DC Voltage": "2.2.3"},
        "i_3phsum_a": {"Avg DC Amps": "2.2.3"},
        "p_mpptsum_kw": {},  # MPPT Cumulative kW
        "p_mppt1_kw": {},  # MPPT kW
        "v_mppt1_v": {},  # MPPT Voltage
        "i_mppt1_a": {},  # MPPT Current
        "t_htsnk_degc": {"Avg Heat Sink Temperature": "2.2.3"},
        "freq_hz": {"Avg AC Frequency": "2.2.3"},
        "SERIAL": {"Serial Number": "2.2.3"},
    },
    METER_DEVICE_TYPE: {
        "freq_hz": {"Avg AC Frequency": "2.2.3"},  # Frequency
        "net_ltea_3phsum_kwh": {"Total Lifetime Energy": "2.2.3"},  # Lifetime Energy
        "p_3phsum_kw": {"Avg Real Power": "2.2.3"},  # "Power"
        "q_3phsum_kvar": {"Avg Reactive Power": "2.2.3"},  # "KVA Reactive"
        "s_3phsum_kva": {"Avg Apparent Power": "2.2.3"},  # "KVA Apparent"
        "tot_pf_rto": {"Avg Power Factor": "2.2.3"},  # "Power Factor"
        "i1_a": {},  # "Leg 1 Amps"
        "i2_a": {},  # "Leg 2 Amps"
        "p1_kw": {},  # "Leg 1 KW"
        "p2_kw": {},  # "Leg 2 KW"
        "v1n_v": {},  # "Leg 1 Volts"
        "v2n_v": {},  # "Leg 2 Volts"
        "v12_v": {},  # "Supply Volts"
        "neg_ltea_3phsum_kwh": {},  # "KWH To Grid"
        "pos_ltea_3phsum_kwh": {},  # "KWH To Home"
        "SERIAL": {"Serial Number": "2.2.3"},
    },
}
