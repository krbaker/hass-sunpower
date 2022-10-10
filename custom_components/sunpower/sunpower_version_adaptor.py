import logging
from typing import Dict, List, Any

from .const import PVS_DEVICE_TYPE, INVERTER_DEVICE_TYPE, METER_DEVICE_TYPE, FIELD_ADAPTORS, SENSOR_CONFIGS
from collections import namedtuple
import re

logger = logging.getLogger(__name__)

KeyValueTup = namedtuple("KeyValueTup", "key value")

DeviceInfo = namedtuple("DeviceInfo", "serial type status name info")


device_serial_type_re = re.compile(r"<h2 id='(\w+)'( type='([\w\-]+)')?")
device_name_re = re.compile(r"<img ?\/><span class='\w*'>([\w;& ]+)<\/span><img ?\/>")
device_status_re = re.compile(r"<span class='\w*'>(\w*)<\/span>")
device_info_re = re.compile(r"<span class='info'>([\w ,\.:]+)<\/span>")

dev_detail_re = re.compile(r"<div class='accordionItem'>(.*)<\/h2><div><table>(.*)<\/table><\/div><\/div>")
date_re = re.compile(r"<span class='DateClass'>([0-9]{4},[0-9]{2},[0-9]{2},[0-9]{2},[0-9]{2},[0-9]{2})<\/span>")


def normalize_html(value: str) -> Any:
    return value.replace("&nbsp;", " ")


def is_number(value: str) -> bool:
    try:
        float(value.strip())
        return True
    except:
        return False


def format_value(value: str) -> Any:
    value = normalize_html(value)
    if "DateClass" in value:
        value = date_re.findall(value)[0]
    if len(value) >= 1 and is_number(value[:-1]):
        if value[-1] == "V":
            value = value[:-1]
    if len(value) >= 2 and is_number(value[:-2]):
        if value[-2:] in ["kB", "kW", "Hz"]:
            value = value[:-2]
    if len(value) >= 3 and is_number(value[:-3]):
        if value[-3:] in ["kWh", "sec", "kVA"]:
            value = value[:-3]
    if len(value) >= 4 and is_number(value[:-4]):
        if value[-4:] in ["kVAR"]:
            value = value[:-4]
    if len(value) >= 6 and is_number(value[:-6]):
        if value[-6:] == "&#176C":
            value = value[:-6]
    return value.strip()


# Lookup map used for auto_format_field_names
FieldVersion = namedtuple("FieldVersion", "field version")
FIELD_LOOKUP_MAP = {}
for device_type, adaptor in FIELD_ADAPTORS.items():
    for expected_field, potential_fields in adaptor.items():
        for potential_field_value, potential_field_version in potential_fields.items():
            FIELD_LOOKUP_MAP.setdefault(device_type, {})[potential_field_value] = FieldVersion(
                expected_field, potential_field_version
            )


def auto_format_field_names(data_obj: dict[str, Any], device_type: str):
    global FIELD_LOOKUP_MAP

    default_field_set = {sensor_config.field for sensor_config in SENSOR_CONFIGS[device_type].values()}
    result = {}

    versions = []
    for given_field, value in data_obj.items():
        if given_field in default_field_set:
            result[given_field] = value
            versions.append("5/6")
        elif given_field in FIELD_LOOKUP_MAP[device_type]:
            versions.append(FIELD_LOOKUP_MAP[device_type][given_field].version)
            result[FIELD_LOOKUP_MAP[device_type][given_field].field] = value
        else:
            logger.debug(f"No field mapping found for {given_field}")

    version_estimates = ", ".join(
        [f"{version}: {len([v for v in versions if v == version])*100 / len(versions):.1f}%" for version in versions]
    )
    logger.info(f"Version Estimate: {version_estimates}")
    return result


def parse_device_list(device_list_result: str):
    device_list = []
    device_str_split = device_list_result.split("<div class='accordionItem'>")[1:]
    for device_html in device_str_split:
        res = device_serial_type_re.findall(device_html)
        if len(res) <= 0:
            raise RuntimeError(f"Unable to parse {device_html} with {device_serial_type_re} for serial & type.")
        serial, _, dev_type = res[0]

        res = device_name_re.findall(device_html)
        if len(res) <= 0:
            raise RuntimeError(f"Unable to parse {device_html} with {device_name_re} for name.")
        name = res[0]

        res = device_status_re.findall(device_html)
        if len(res) <= 0:
            raise RuntimeError(f"Unable to parse {device_html} with {device_status_re} for status.")
        status = res[0]

        res = device_info_re.findall(device_html)
        if len(res) <= 0:
            raise RuntimeError(f"Unable to parse {device_html} with {device_info_re} for status.")
        info = res[0]
        device = DeviceInfo(*[normalize_html(arg) for arg in [serial, dev_type, status, name, info]])
        device_list.append(device)
    return device_list


def parse_device_info(device_info_result: str, device_summary: DeviceInfo) -> Dict[str, str]:
    search_result = dev_detail_re.findall(device_info_result)

    # validate the result
    if len(search_result) <= 0:
        raise RuntimeError("Unsupported Version of Sunpower PVS")

    # extract the detail section
    _, detail = search_result[0]
    # Make the string easier to work with
    stripped = (
        detail.replace("</tr>", "").replace("<b>", "").replace("</b>", "").replace("&nbsp;", " ").replace("</td>", "")
    )

    # generate pairs of data. Most data will be ready to use, but some, like dates, are still
    # going to need further refining after this step.
    data_pairs = [
        KeyValueTup(*key_value)
        for key_value in [
            val.replace(" class='working'>", "").replace(" class='info'>", "").replace(" class='error'", "").split(":")
            for tr in stripped.split("<tr>")[1:]
            for val in tr.split("<td")[1:]
        ]
        if len(key_value) == 2
    ]
    # Convert to a dictionary
    data = {normalize_html(data.key): format_value(data.value) for data in data_pairs}

    # Infer the device type
    if "Avg CPU Load" in data:
        additional_data = {
            "DEVICE_TYPE": PVS_DEVICE_TYPE,
        }
    elif "Avg Heat Sink Temperature" in data:
        additional_data = {
            "DEVICE_TYPE": INVERTER_DEVICE_TYPE,
            "TYPE": device_summary.type,
            "DESCR": device_summary.name,
        }
    else:
        additional_data = {
            "DEVICE_TYPE": METER_DEVICE_TYPE,
            "TYPE": device_summary.type,
            "DESCR": device_summary.name,
        }
    device_detail = auto_format_field_names(data, additional_data["DEVICE_TYPE"])
    device_detail.update(additional_data)
    device_detail.update({"STATE": device_summary.status})
    if "p_3phsum_kw" not in device_detail:
        device_detail["p_3phsum_kw"] = float(device_detail["vln_3phavg_v"]) * float(device_detail["avg_dc_current"])
    return device_detail
