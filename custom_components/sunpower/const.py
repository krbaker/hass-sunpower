"""Constants for the sunpower integration."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfInformation,
    UnitOfPower,
    UnitOfReactivePower,
    UnitOfTemperature,
    UnitOfTime,
)

DOMAIN = "sunpower"

SUNPOWER_DESCRIPTIVE_NAMES = "use_descriptive_names"
SUNPOWER_PRODUCT_NAMES = "use_product_names"
SUNPOWER_OBJECT = "sunpower"
SUNPOWER_HOST = "host"
SUNPOWER_COORDINATOR = "coordinator"
DEFAULT_SUNPOWER_UPDATE_INTERVAL = 120
DEFAULT_SUNVAULT_UPDATE_INTERVAL = 60
MIN_SUNPOWER_UPDATE_INTERVAL = 60
MIN_SUNVAULT_UPDATE_INTERVAL = 20
SUNPOWER_UPDATE_INTERVAL = "PVS_UPDATE_INTERVAL"
SUNVAULT_UPDATE_INTERVAL = "ESS_UPDATE_INTERVAL"
SETUP_TIMEOUT_MIN = 5

PVS_DEVICE_TYPE = "PVS"
INVERTER_DEVICE_TYPE = "Inverter"
METER_DEVICE_TYPE = "Power Meter"
BATTERY_DEVICE_TYPE = "ESS BMS"
ESS_DEVICE_TYPE = "Energy Storage System"
HUBPLUS_DEVICE_TYPE = "HUB+"
SUNVAULT_DEVICE_TYPE = "SunVault"

WORKING_STATE = "working"

# SUNPOWER_DESCRIPTIVE_NAMES will take advantage of the following:
# - {SUN_POWER} is replaced with "SunPower "
# - {TYPE} is replaced with "{data['TYPE']} " if available otherwise ""
# - {DESCR} is replaced with "{data['DESCR']} " if available otherwise ""
# - {PVS} is replaced with "PVS "
# - {index} is replaced with "{device_type_index} " if available otherwise ""
# - {SUN_VAULT} is replaced with "SunVault "
# - {SERIAL} is replaced with the raw device serial # (no spaces)
# - {MODEL} is replaced with the raw device MODEL (no spaces)


SUNPOWER_BINARY_SENSORS = {
    METER_DEVICE_TYPE: {
        "unique_id": "meter",
        "sensors": {
            "METER_STATE": {
                "field": "STATE",
                "title": "{SUN_POWER}{DESCR}State",
                "device": SensorDeviceClass.POWER,
                "on_value": WORKING_STATE,
            },
        },
    },
    INVERTER_DEVICE_TYPE: {
        "unique_id": "inverter",
        "sensors": {
            "INVERTER_STATE": {
                "field": "STATE",
                "title": "{SUN_POWER}{DESCR}State",
                "device": SensorDeviceClass.POWER,
                "on_value": WORKING_STATE,
            },
        },
    },
    PVS_DEVICE_TYPE: {
        "unique_id": "pvs",
        "sensors": {
            "PVS_STATE": {
                "field": "STATE",
                "title": "{SUN_POWER}{MODEL} {SERIAL} State",
                "device": SensorDeviceClass.POWER,
                "on_value": WORKING_STATE,
            },
        },
    },
}

SUNVAULT_BINARY_SENSORS = {
    HUBPLUS_DEVICE_TYPE: {
        "unique_id": "hubplus",
        "sensors": {
            "HUBPLUS_STATE": {
                "field": "STATE",
                "title": "{SUN_POWER}Hub Plus State",
                "device": SensorDeviceClass.POWER,
                "on_value": WORKING_STATE,
            },
        },
    },
    ESS_DEVICE_TYPE: {
        "unique_id": "ess",
        "sensors": {
            "ESS_STATE": {
                "field": "STATE",
                "title": "{SUN_VAULT}ESS {index}State",
                "device": SensorDeviceClass.POWER,
                "on_value": WORKING_STATE,
            },
        },
    },
    BATTERY_DEVICE_TYPE: {
        "unique_id": "battery",
        "sensors": {
            "BATTERY_STATE": {
                "field": "STATE",
                "title": "{SUN_VAULT}Battery {index}State",
                "device": SensorDeviceClass.POWER,
                "on_value": WORKING_STATE,
            },
        },
    },
    SUNVAULT_DEVICE_TYPE: {
        "unique_id": "sunvault",
        "sensors": {
            "SUNVAULT_STATE": {
                "field": "STATE",
                "title": "{SUN_VAULT}State",
                "device": SensorDeviceClass.POWER,
                "on_value": WORKING_STATE,
            },
        },
    },
}

SUNPOWER_SENSORS = {
    PVS_DEVICE_TYPE: {
        "unique_id": "pvs",
        "sensors": {
            "PVS_LOAD": {
                "field": "dl_cpu_load",
                "title": "{SUN_POWER}{MODEL} {SERIAL} System Load",
                "unit": "",
                "icon": "mdi:gauge",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "PVS_ERROR_COUNT": {
                "field": "dl_err_count",
                "title": "{SUN_POWER}{MODEL} {SERIAL} Error Count",
                "unit": "",
                "icon": "mdi:alert-circle",
                "device": None,
                "state": SensorStateClass.TOTAL,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "PVS_COMMUNICATION_ERRORS": {
                "field": "dl_comm_err",
                "title": "{SUN_POWER}{MODEL} {SERIAL} Communication Errors",
                "unit": "",
                "icon": "mdi:network-off",
                "device": None,
                "state": SensorStateClass.TOTAL,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "PVS_SKIPPED_SCANS": {
                "field": "dl_skipped_scans",
                "title": "{SUN_POWER}{MODEL} {SERIAL} Skipped Scans",
                "unit": "",
                "icon": "mdi:network-strength-off-outline",
                "device": None,
                "state": SensorStateClass.TOTAL_INCREASING,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "PVS_SCAN_TIME": {
                "field": "dl_scan_time",
                "title": "{SUN_POWER}{MODEL} {SERIAL} Scan Time",
                "unit": UnitOfTime.SECONDS,
                "icon": "mdi:timer-outline",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "PVS_UNTRANSMITTED": {
                "field": "dl_untransmitted",
                "title": "{SUN_POWER}{MODEL} {SERIAL} Untransmitted Data",
                "unit": "",
                "icon": "mdi:radio-tower",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "PVS_UPTIME": {
                "field": "dl_uptime",
                "title": "{SUN_POWER}{MODEL} {SERIAL} Uptime",
                "unit": UnitOfTime.SECONDS,
                "icon": "mdi:timer-outline",
                "device": None,
                "state": SensorStateClass.TOTAL_INCREASING,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "PVS_MEMORY_USED": {
                "field": "dl_mem_used",
                "title": "{SUN_POWER}{MODEL} {SERIAL} Memory Used",
                "unit": UnitOfInformation.KILOBYTES,
                "icon": "mdi:memory",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "PVS_FLASH_AVAILABLE": {
                "field": "dl_flash_avail",
                "title": "{SUN_POWER}{MODEL} {SERIAL} Flash Available",
                "unit": UnitOfInformation.KILOBYTES,
                "icon": "mdi:memory",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
        },
    },
    METER_DEVICE_TYPE: {
        "unique_id": "meter",
        "sensors": {
            "METER_FREQUENCY": {
                "field": "freq_hz",
                "title": "{SUN_POWER}{DESCR}Frequency",
                "unit": UnitOfFrequency.HERTZ,
                "icon": "mdi:flash",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
            },
            "METER_NET_KWH": {
                "field": "net_ltea_3phsum_kwh",
                "title": "{SUN_POWER}{DESCR}Lifetime Power",
                "unit": UnitOfEnergy.KILO_WATT_HOUR,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.ENERGY,
                "state": SensorStateClass.TOTAL,
            },
            "METER_KW": {
                "field": "p_3phsum_kw",
                "title": "{SUN_POWER}{DESCR}Power",
                "unit": UnitOfPower.KILO_WATT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.POWER,
                "state": SensorStateClass.MEASUREMENT,
            },
            "METER_VAR": {
                "field": "q_3phsum_kvar",
                "title": "{SUN_POWER}{DESCR}KVA Reactive",
                "unit": UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
                "icon": "mdi:flash",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "METER_VA": {
                "field": "s_3phsum_kva",
                "title": "{SUN_POWER}{DESCR}KVA Apparent",
                "unit": UnitOfApparentPower.VOLT_AMPERE,
                "icon": "mdi:flash",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "METER_POWER_FACTOR": {
                "field": "tot_pf_rto",
                "title": "{SUN_POWER}{DESCR}Power Factor",
                "unit": PERCENTAGE,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.POWER_FACTOR,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "METER_L1_A": {
                "field": "i1_a",
                "title": "{SUN_POWER}{DESCR}Leg 1 Amps",
                "unit": UnitOfElectricCurrent.AMPERE,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.CURRENT,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "METER_A": {
                "field": "i_a",
                "title": "{SUN_POWER}{DESCR}Amps",
                "unit": UnitOfElectricCurrent.AMPERE,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.CURRENT,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "METER_L2_A": {
                "field": "i2_a",
                "title": "{SUN_POWER}{DESCR}Leg 2 Amps",
                "unit": UnitOfElectricCurrent.AMPERE,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.CURRENT,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "METER_L1_KW": {
                "field": "p1_kw",
                "title": "{SUN_POWER}{DESCR}Leg 1 KW",
                "unit": UnitOfPower.KILO_WATT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.POWER,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "METER_L2_KW": {
                "field": "p2_kw",
                "title": "{SUN_POWER}{DESCR}Leg 2 KW",
                "unit": UnitOfPower.KILO_WATT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.POWER,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "METER_L1_V": {
                "field": "v1n_v",
                "title": "{SUN_POWER}{DESCR}Leg 1 Volts",
                "unit": UnitOfElectricPotential.VOLT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.VOLTAGE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "METER_L2_V": {
                "field": "v2n_v",
                "title": "{SUN_POWER}{DESCR}Leg 2 Volts",
                "unit": UnitOfElectricPotential.VOLT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.VOLTAGE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "METER_L12_V": {
                "field": "v12_v",
                "title": "{SUN_POWER}{DESCR}Supply Volts",
                "unit": UnitOfElectricPotential.VOLT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.VOLTAGE,
                "state": SensorStateClass.MEASUREMENT,
            },
            "METER_TO_GRID": {
                "field": "neg_ltea_3phsum_kwh",
                "title": "{SUN_POWER}{DESCR}KWh To Grid",
                "unit": UnitOfEnergy.KILO_WATT_HOUR,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.ENERGY,
                "state": SensorStateClass.TOTAL,
            },
            "METER_TO_HOME": {
                "field": "pos_ltea_3phsum_kwh",
                "title": "{SUN_POWER}{DESCR}KWh To Home",
                "unit": UnitOfEnergy.KILO_WATT_HOUR,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.ENERGY,
                "state": SensorStateClass.TOTAL_INCREASING,
            },
        },
    },
    INVERTER_DEVICE_TYPE: {
        "unique_id": "inverter",
        "sensors": {
            "INVERTER_NET_KWH": {
                "field": "ltea_3phsum_kwh",
                "title": "{SUN_POWER}{DESCR}Lifetime Power",
                "unit": UnitOfEnergy.KILO_WATT_HOUR,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.ENERGY,
                "state": SensorStateClass.TOTAL,
            },
            "INVERTER_KW": {
                "field": "p_3phsum_kw",
                "title": "{SUN_POWER}{DESCR}Power",
                "unit": UnitOfPower.KILO_WATT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.POWER,
                "state": SensorStateClass.MEASUREMENT,
            },
            "INVERTER_VOLTS": {
                "field": "vln_3phavg_v",
                "title": "{SUN_POWER}{DESCR}Voltage",
                "unit": UnitOfElectricPotential.VOLT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.VOLTAGE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "INVERTER_AMPS": {
                "field": "i_3phsum_a",
                "title": "{SUN_POWER}{DESCR}Amps",
                "unit": UnitOfElectricCurrent.AMPERE,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.CURRENT,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "INVERTER_MPPT_KW": {
                "field": "p_mpptsum_kw",
                "title": "{SUN_POWER}{DESCR}MPPT Sum KW",
                "unit": UnitOfPower.KILO_WATT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.POWER,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "INVERTER_MPPT1_KW": {
                "field": "p_mppt1_kw",
                "title": "{SUN_POWER}{DESCR}MPPT KW",
                "unit": UnitOfPower.KILO_WATT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.POWER,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "INVERTER_MPPT_V": {
                "field": "v_mppt1_v",
                "title": "{SUN_POWER}{DESCR}MPPT Volts",
                "unit": UnitOfElectricPotential.VOLT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.VOLTAGE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "INVERTER_MPPT_A": {
                "field": "i_mppt1_a",
                "title": "{SUN_POWER}{DESCR}MPPT Amps",
                "unit": UnitOfElectricCurrent.AMPERE,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.CURRENT,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "INVERTER_TEMPERATURE": {
                "field": "t_htsnk_degc",
                "title": "{SUN_POWER}{DESCR}Temperature",
                "unit": UnitOfTemperature.CELSIUS,
                "icon": "mdi:thermometer",
                "device": SensorDeviceClass.TEMPERATURE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "INVERTER_FREQUENCY": {
                "field": "freq_hz",
                "title": "{SUN_POWER}{DESCR}Frequency",
                "unit": UnitOfFrequency.HERTZ,
                "icon": "mdi:flash",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
        },
    },
}

SUNVAULT_SENSORS = {
    SUNVAULT_DEVICE_TYPE: {
        "unique_id": "sunvault",
        "sensors": {
            "SUNVAULT_AMPERAGE": {
                "field": "sunvault_amperage",
                "title": "{SUN_VAULT}Amps",
                "unit": UnitOfElectricCurrent.AMPERE,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.CURRENT,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "SUNVAULT_VOLTAGE": {
                "field": "sunvault_voltage",
                "title": "{SUN_VAULT}Voltage",
                "unit": UnitOfElectricPotential.VOLT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.VOLTAGE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "SUNVAULT_TEMPERATURE": {
                "field": "sunvault_temperature",
                "title": "{SUN_VAULT}Temperature",
                "unit": UnitOfTemperature.CELSIUS,
                "icon": "mdi:thermometer",
                "device": SensorDeviceClass.TEMPERATURE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "SUNVAULT_CUSTOMER_STATE_OF_CHARGE": {
                "field": "sunvault_customer_state_of_charge",
                "title": "{SUN_VAULT}Customer State of Charge",
                "unit": PERCENTAGE,
                "icon": "mdi:battery-charging-100",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
            },
            "SUNVAULT_SYSTEM_STATE_OF_CHARGE": {
                "field": "sunvault_system_state_of_charge",
                "title": "{SUN_VAULT}System State of Charge",
                "unit": PERCENTAGE,
                "icon": "mdi:battery-charging-100",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "SUNVAULT_POWER": {
                "field": "sunvault_power",
                "title": "{SUN_VAULT}Power",
                "unit": UnitOfPower.WATT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.POWER,
                "state": SensorStateClass.MEASUREMENT,
            },
            "SUNVAULT_POWER_INPUT": {
                "field": "sunvault_power_input",
                "title": "{SUN_VAULT}Power Input",
                "unit": UnitOfPower.WATT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.POWER,
                "state": SensorStateClass.MEASUREMENT,
            },
            "SUNVAULT_POWER_OUTPUT": {
                "field": "sunvault_power_output",
                "title": "{SUN_VAULT}Power Output",
                "unit": UnitOfPower.WATT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.POWER,
                "state": SensorStateClass.MEASUREMENT,
            },
        },
    },
    HUBPLUS_DEVICE_TYPE: {
        "unique_id": "hubplus",
        "sensors": {
            # "HUBPLUS_CONTACTOR_POSITION": [
            #     "contactor_position",
            #     "Contactor Position",
            #     "",
            #     "mdi:electric-switch",
            #     None,
            #     SensorStateClass.MEASUREMENT
            #     ],
            # "HUBPLUS_GRID_FREQUENCY_STATE": [
            #     "grid_frequency_state",
            #     "Grid Frequency State",
            #     "",
            #     "mdi:state-machine",
            #     None,
            #     SensorStateClass.MEASUREMENT
            #     ],
            "HUBPLUS_GRID_P1_V": {
                "field": "grid_phase1_voltage",
                "title": "{SUN_POWER}HUB Plus Grid Phase 1 Voltage",
                "unit": UnitOfElectricPotential.VOLT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.VOLTAGE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "HUBPLUS_GRID_P2_V": {
                "field": "grid_phase2_voltage",
                "title": "{SUN_POWER}HUB Plus Grid Phase 2 Voltage",
                "unit": UnitOfElectricPotential.VOLT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.VOLTAGE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            # "HUBPLUS_GRID_VOLTAGE_STATE": [
            #     "grid_voltage_state",
            #     "Grid Voltage State",
            #     "",
            #     "mdi:state-machine",
            #     None,
            #     SensorStateClass.MEASUREMENT
            #     ],
            "HUBPLUS_HUMIDITY": {
                "field": "hub_humidity",
                "title": "{SUN_POWER}HUB Plus Humidity",
                "unit": PERCENTAGE,
                "icon": "mdi:water-percent",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "HUBPLUS_TEMPERATURE": {
                "field": "hub_temperature",
                "title": "{SUN_POWER}HUB Plus Temperature",
                "unit": UnitOfTemperature.CELSIUS,
                "icon": "mdi:thermometer",
                "device": SensorDeviceClass.TEMPERATURE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            # "HUBPLUS_LOAD_FREQUENCY_STATE": [
            #     "load_frequency_state",
            #     "Load Frequency State",
            #     "",
            #     "mdi:state-machine",
            #     None,
            #     SensorStateClass.MEASUREMENT
            #     ],
            "HUBPLUS_LOAD_P1_V": {
                "field": "load_phase1_voltage",
                "title": "{SUN_POWER}HUB Plus Load Phase 1 Voltage",
                "unit": UnitOfElectricPotential.VOLT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.VOLTAGE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "HUBPLUS_LOAD_P2_V": {
                "field": "load_phase2_voltage",
                "title": "{SUN_POWER}HUB Plus Load Phase 2 Voltage",
                "unit": UnitOfElectricPotential.VOLT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.VOLTAGE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            # "HUBPLUS_LOAD_VOLTAGE_STATE": [
            #     "load_voltage_state",
            #     "Load Voltage State",
            #     "",
            #     "mdi:state-machine",
            #     None,
            #     SensorStateClass.MEASUREMENT
            #     ],
            # "HUBPLUS_MAIN_VOLTAGE": [
            #     "main_voltage",
            #     "HUB Plus Main Voltage",
            #     UnitOfElectricPotential.VOLT,
            #     "mdi:flash",
            #     SensorDeviceClass.VOLTAGE,
            #     SensorStateClass.MEASUREMENT
            #     ]
        },
    },
    BATTERY_DEVICE_TYPE: {
        "unique_id": "battery",
        "sensors": {
            "BATTERY_AMPERAGE": {
                "field": "battery_amperage",
                "title": "{SUN_VAULT}Battery {index}Amps",
                "unit": UnitOfElectricCurrent.AMPERE,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.CURRENT,
                "state": SensorStateClass.MEASUREMENT,
            },
            "BATTERY_VOLTAGE": {
                "field": "battery_voltage",
                "title": "{SUN_VAULT}Battery {index}Voltage",
                "unit": UnitOfElectricPotential.VOLT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.VOLTAGE,
                "state": SensorStateClass.MEASUREMENT,
            },
            "BATTERY_TEMPERATURE": {
                "field": "temperature",
                "title": "{SUN_VAULT}Battery {index}Temperature",
                "unit": UnitOfTemperature.CELSIUS,
                "icon": "mdi:thermometer",
                "device": SensorDeviceClass.TEMPERATURE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "BATTERY_CUSTOMER_STATE_OF_CHARGE": {
                "field": "customer_state_of_charge",
                "title": "{SUN_VAULT}Battery {index}Customer State of Charge",
                "unit": PERCENTAGE,
                "icon": "mdi:battery-charging-100",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
            },
            "BATTERY_SYSTEM_STATE_OF_CHARGE": {
                "field": "system_state_of_charge",
                "title": "{SUN_VAULT}Battery {index}System State of Charge",
                "unit": PERCENTAGE,
                "icon": "mdi:battery-charging-100",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
        },
    },
    ESS_DEVICE_TYPE: {
        "unique_id": "ess",
        "sensors": {
            "ESS_HUMIDITY": {
                "field": "enclosure_humidity",
                "title": "{SUN_VAULT}ESS {index}Humidity",
                "unit": PERCENTAGE,
                "icon": "mdi:water-percent",
                "device": None,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "ESS_TEMPERATURE": {
                "field": "enclosure_temperature",
                "title": "{SUN_VAULT}ESS {index}Temperature",
                "unit": UnitOfTemperature.CELSIUS,
                "icon": "mdi:thermometer",
                "device": SensorDeviceClass.TEMPERATURE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "ESS_POWER": {
                "field": "agg_power",
                "title": "{SUN_VAULT}ESS {index}Power",
                "unit": UnitOfPower.KILO_WATT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.POWER,
                "state": SensorStateClass.MEASUREMENT,
            },
            "ESS_METER_A_A": {
                "field": "meter_a_current",
                "title": "{SUN_VAULT}ESS {index}Meter A Amps",
                "unit": UnitOfElectricCurrent.AMPERE,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.CURRENT,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "ESS_METER_A_W": {
                "field": "meter_a_power",
                "title": "{SUN_VAULT}ESS {index}Meter A Power",
                "unit": UnitOfPower.WATT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.POWER,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "ESS_METER_A_V": {
                "field": "meter_a_voltage",
                "title": "{SUN_VAULT}ESS {index}Meter A Voltage",
                "unit": UnitOfElectricPotential.VOLT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.VOLTAGE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "ESS_METER_B_A": {
                "field": "meter_b_current",
                "title": "{SUN_VAULT}ESS {index}Meter B Amps",
                "unit": UnitOfElectricCurrent.AMPERE,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.CURRENT,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "ESS_METER_B_W": {
                "field": "meter_b_power",
                "title": "{SUN_VAULT}ESS {index}Meter B Power",
                "unit": UnitOfPower.WATT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.POWER,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
            "ESS_METER_B_V": {
                "field": "meter_b_voltage",
                "title": "{SUN_VAULT}ESS {index}Meter B Voltage",
                "unit": UnitOfElectricPotential.VOLT,
                "icon": "mdi:flash",
                "device": SensorDeviceClass.VOLTAGE,
                "state": SensorStateClass.MEASUREMENT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
        },
    },
}
