"""Constants for the sunpower integration."""
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
)

from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass

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

METER_SENSORS = {
    "METER_FREQUENCY": ["freq_hz", "Frequency", FREQUENCY_HERTZ, "mdi:flash",
                        None, SensorStateClass.MEASUREMENT],
    "METER_NET_KWH": [
        "net_ltea_3phsum_kwh",
        "Lifetime Power",
        ENERGY_KILO_WATT_HOUR,
        "mdi:flash",
        SensorDeviceClass.ENERGY, SensorStateClass.TOTAL,
    ],
    "METER_KW": ["p_3phsum_kw", "Power", POWER_KILO_WATT, "mdi:flash",
                 SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT],
    "METER_VAR": ["q_3phsum_kvar", "KVA Reactive", POWER_VOLT_AMPERE, "mdi:flash",
                  None, SensorStateClass.MEASUREMENT],
    "METER_VA": ["s_3phsum_kva", "KVA Apparent", POWER_VOLT_AMPERE, "mdi:flash",
                 None, SensorStateClass.MEASUREMENT],
    "METER_POWER_FACTOR": ["tot_pf_rto", "Power Factor", PERCENTAGE, "mdi:flash",
                           SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT],
    "METER_L1_A": ["i1_a", "Leg 1 Amps", ELECTRIC_CURRENT_AMPERE, "mdi:flash",
                   SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT],
    "METER_A": ["i_a", "Amps", ELECTRIC_CURRENT_AMPERE, "mdi:flash",
                   SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT],
    "METER_L2_A": ["i2_a", "Leg 2 Amps", ELECTRIC_CURRENT_AMPERE, "mdi:flash",
                   SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT],
    "METER_L1_KW": ["p1_kw", "Leg 1 KW", POWER_KILO_WATT, "mdi:flash",
                    SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT],
    "METER_L2_KW": ["p2_kw", "Leg 2 KW", POWER_KILO_WATT, "mdi:flash",
                    SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT],
    "METER_L1_V": ["v1n_v", "Leg 1 Volts", ELECTRIC_POTENTIAL_VOLT, "mdi:flash",
                   SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT],
    "METER_L2_V": ["v2n_v", "Leg 2 Volts", ELECTRIC_POTENTIAL_VOLT, "mdi:flash",
                   SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT],
    "METER_L12_V": ["v12_v", "Supply Volts", ELECTRIC_POTENTIAL_VOLT, "mdi:flash",
                    SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT],
    "METER_TO_GRID": ["neg_ltea_3phsum_kwh", "KWH To Grid", ENERGY_KILO_WATT_HOUR, "mdi:flash",
                      SensorDeviceClass.ENERGY, SensorStateClass.TOTAL],
    "METER_TO_HOME": ["pos_ltea_3phsum_kwh", "KWH To Home", ENERGY_KILO_WATT_HOUR, "mdi:flash",
                      SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING]
}

INVERTER_SENSORS = {
    "INVERTER_NET_KWH": [
        "ltea_3phsum_kwh",
        "Lifetime Power",
        ENERGY_KILO_WATT_HOUR,
        "mdi:flash",
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING
    ],
    "INVERTER_KW": ["p_3phsum_kw", "Power", POWER_KILO_WATT, "mdi:flash",
                    SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT],
    "INVERTER_VOLTS": ["vln_3phavg_v", "Voltage", ELECTRIC_POTENTIAL_VOLT, "mdi:flash",
                       SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT],
    "INVERTER_AMPS": ["i_3phsum_a", "Amps", ELECTRIC_CURRENT_AMPERE, "mdi:flash",
                      SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT],
    "INVERTER_MPPT_KW": ["p_mpptsum_kw", "MPPT KW", POWER_KILO_WATT, "mdi:flash",
                         SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT],
    "INVERTER_MPPT1_KW": ["p_mppt1_kw", "MPPT KW", POWER_KILO_WATT, "mdi:flash",
                          SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT],
    "INVERTER_MPPT_V": ["v_mppt1_v", "MPPT Volts", ELECTRIC_POTENTIAL_VOLT, "mdi:flash",
                        SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT],
    "INVERTER_MPPT_A": ["i_mppt1_a", "MPPT Amps", ELECTRIC_CURRENT_AMPERE, "mdi:flash",
                        SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT],
    "INVERTER_TEMPERATURE": [
        "t_htsnk_degc",
        "Temperature",
        TEMP_CELSIUS,
        "mdi:thermometer",
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT
    ],
    "INVERTER_FREQUENCY": ["freq_hz", "Frequency", FREQUENCY_HERTZ, "mdi:flash",
                           None, SensorStateClass.MEASUREMENT],
}

PVS_SENSORS = {
    "PVS_LOAD": [
        "dl_cpu_load",
        "System Load",
        "",
        "mdi:gauge",
        None,
        SensorStateClass.MEASUREMENT
        ],
    "PVS_ERROR_COUNT": [
        "dl_err_count",
        "Error Count",
        "",
        "mdi:alert-circle",
        None,
        SensorStateClass.TOTAL
        ],
    "PVS_COMMUNICATION_ERRORS": [
        "dl_comm_err",
        "Communication Errors",
        "",
        "mdi:network-off",
        None,
        SensorStateClass.TOTAL
        ],
    "PVS_SKIPPED_SCANS": [
        "dl_skipped_scans",
        "Skipped Scans",
        "",
        "mdi:network-strength-off-outline",
        None,
        SensorStateClass.TOTAL_INCREASING
        ],
    "PVS_SCAN_TIME": [
        "dl_scan_time",
        "Scan Time",
        TIME_SECONDS,
        "mdi:timer-outline",
        None,
        SensorStateClass.MEASUREMENT
        ],
    "PVS_UNTRANSMITTED": [
        "dl_untransmitted",
        "Untransmitted Data",
        "",
        "mdi:radio-tower",
        None,
        SensorStateClass.MEASUREMENT
        ],
    "PVS_UPTIME": [
        "dl_uptime",
        "Uptime",
        TIME_SECONDS,
        "mdi:timer-outline",
        None,
        SensorStateClass.TOTAL_INCREASING
        ],
    "PVS_MEMORY_USED": [
        "dl_mem_used",
        "Memory Used",
        DATA_KILOBYTES,
        "mdi:memory",
        None,
        SensorStateClass.MEASUREMENT
        ],
    "PVS_FLASH_AVAILABLE": [
        "dl_flash_avail",
        "Flash Available",
        DATA_KILOBYTES,
        "mdi:memory",
        None,
        SensorStateClass.MEASUREMENT
        ],
}
