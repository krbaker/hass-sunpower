import logging
from typing import Dict, List, Any

from .const import PVS_DEVICE_TYPE, INVERTER_DEVICE_TYPE, METER_DEVICE_TYPE, FIELD_ADAPTORS, SENSOR_CONFIGS
from collections import namedtuple
import re

logger = logging.getLogger(__name__)

device_list_item = namedtuple("device_list_item", "serial x type y z error working name info link")
key_value_tup = namedtuple("key_value_tup", "key value")


device_list_item_re = re.compile(
    r"<div class='accordionItem'><h2 id='([A-Z0-9]+)'( type='([a-zA-Z0-9\-]+)')*><img\/><span class='(working)?(error)?'>([a-zA-Z0-9 ]+)<\/span><img\/>(<span class='error'>Error</span>)?(<span class='working'>Working<\/span>)?<span class='info'>([ a-zA-Z,0-9\.]+)<\/span><span class='link'>([a-zA-Z0-9\-]*)<\/span><\/h2><div><\/div><\/div>"
)
dev_detail_re = re.compile(r"<div class='accordionItem'>(.*)<\/h2><div><table>(.*)<\/table><\/div><\/div>")
date_re = re.compile(r"<span class='DateClass'>([0-9]{4},[0-9]{2},[0-9]{2},[0-9]{2},[0-9]{2},[0-9]{2})<\/span>")


def format_value(value: str) -> Any:
    if "DateClass" in value:
        value = date_re.findall(value)[0]
    if len(value) >= 1 and str.isdecimal(value[:-1].replace(".", "")):
        if value[-1] == "V":
            value = value[:-1]
    if len(value) >= 2 and str.isdecimal(value[:-2].replace(".", "")):
        if value[-2:] in ["kB", "kW", "Hz"]:
            value = value[:-2]
    if len(value) >= 3 and str.isdecimal(value[:-3].replace(".", "")):
        if value[-3:] in ["kWh", "sec"]:
            value = value[:-3]
    if len(value) >= 6 and str.isdecimal(value[:-6].replace(".", "")):
        if value[-6:] == "&#176C":
            value = value[:-6]
    return value


def parse_device_list(command_result: str) -> List[device_list_item]:
    devices = device_list_item_re.findall(command_result)
    return [device_list_item(*device_tuple) for device_tuple in devices]


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
            logger.warn(f"No field mapping found for {given_field}")

    version_estimates = ", ".join(
        [f"{version}: {len([v for v in versions if v == version])*100 / len(versions):.1f}%" for version in versions]
    )
    logger.info(f"Version Estimate: {version_estimates}")
    return result


def parse_device_info(device_info_result: str) -> Dict[str, str]:
    search_result = dev_detail_re.findall(device_info_result)

    # validate the result
    if len(search_result) <= 0:
        raise RuntimeError("Unsupported Version of Sunpower PVS")

    # extract the detail section
    _, detail = search_result[0]

    # Make the string easier to work with
    stripped = (
        detail.replace("</tr>", "").replace("<b>", "").replace("</b>", "").replace("&nbsp;", "").replace("</td>", "")
    )

    # generate pairs of data. Most data will be ready to use, but some, like dates, are still
    # going to need further refining after this step.
    data_pairs = [
        key_value_tup(*key_value)
        for key_value in [
            val.replace(" class='working'>", "").replace(" class='info'>", "").replace(" class='error'", "").split(":")
            for tr in stripped.split("<tr>")[1:]
            for val in tr.split("<td")[1:]
        ]
        if len(key_value) == 2
    ]
    # Convert to a dictionary
    data = {data.key: format_value(data.value) for data in data_pairs}

    # Infer the device type
    if "Avg CPU Load" in data:
        device_type = PVS_DEVICE_TYPE
    elif "Avg Heat Sink Temperature" in data:
        device_type = INVERTER_DEVICE_TYPE
    else:
        device_type = METER_DEVICE_TYPE

    return {device_type: auto_format_field_names(data, device_type)}
