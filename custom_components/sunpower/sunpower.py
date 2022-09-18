""" Basic Sunpower PVS Tool """
import requests

from .sunpower_version_adaptor import parse_device_list, parse_device_info


class ConnectionException(Exception):
    """Any failure to connect to sunpower PVS"""


class SunPowerMonitor:
    """Basic Class to talk to sunpower pvs 2/5/6 via the management interface 'API'.  This is not a public API so it might fail at any time.
    if you find this usefull please complain to sunpower and your sunpower dealer that they
    do not have a public API"""

    def __init__(self, host: str):
        """Initialize."""
        self._host = host

    def generic_command(self, command):
        """All 'commands' to the PVS module use this url pattern and return json
        The PVS system can take a very long time to respond so timeout is at 2 minutes"""
        try:
            response = requests.get(f"http://{self._host}/cgi-bin/dl_cgi?Command={command}", timeout=120)
        except requests.exceptions.RequestException as error:
            raise ConnectionException from error

        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError:
            # SW Version 2.x.x of Sunpower PVS return data embedded in http.  Return the raw
            # string for processing via regular expressions.
            result = response.text
        return result

    def command_with_arguments(self, command, **kwargs):
        args = "".join([f"&{key}={value}" for key, value in kwargs.items()])

        try:
            response = requests.get(f"http://{self._host}/cgi-bin/dl_cgi?Command={command}{args}", timeout=120)
        except requests.exceptions.RequestException as error:
            raise ConnectionException from error

        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError:
            # SW Version 2.x.x of Sunpower PVS return data embedded in http.  Return the raw
            # string for processing via regular expressions.
            result = response.text
        return result

    def device_list(self):
        """Get a list of all devices connected to the PVS"""
        command_result = self.generic_command("DeviceList")

        # If the api did not return a json, the raw string is returned, and must be parsed manually
        if isinstance(command_result, str):
            device_list_raw = parse_device_list(command_result)
            device_list = {"devices": []}
            for device in device_list_raw:
                device_info_result = self.command_with_arguments("DeviceDetails", SerialNumber=device.serial)
                device_list["devices"].append(parse_device_info(device_info_result, device))

        # For the case of api that does return json, the results can just be passed along directly
        else:
            device_list = command_result

        for device in device_list["devices"]:
            device["STATE"] = "active" if device["STATE"].lower() == "working" else "inactive"

        return device_list

    def network_status(self):
        """Get a list of network interfaces on the PVS"""
        command_result = self.generic_command("Get_Comm")
        if isinstance(command_result, dict):
            return command_result
