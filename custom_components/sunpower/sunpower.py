""" Basic Sunpower PVS Tool """
import requests
import simplejson

class ConnectionException(Exception):
    """Any failure to connect to sunpower PVS"""

class ParseException(Exception):
    """Any failure to connect to sunpower PVS"""


class SunPowerMonitor:
    """Basic Class to talk to sunpower pvs 5/6 via the management interface 'API'.  This is not a public API so it might fail at any time.
    if you find this usefull please complain to sunpower and your sunpower dealer that they
    do not have a public API"""

    def __init__(self, host):
        """Initialize."""
        self.host = host
        self.command_url = "http://{0}/cgi-bin/dl_cgi?Command=".format(host)

    def generic_command(self, command):
        """All 'commands' to the PVS module use this url pattern and return json
        The PVS system can take a very long time to respond so timeout is at 2 minutes"""
        try:
            return requests.get(self.command_url + command, timeout=120).json()
        except requests.exceptions.RequestException as error:
            raise ConnectionException from error
        except simplejson.errors.JSONDecodeError as error:
            raise ParseException from error
        
    def device_list(self):
        """Get a list of all devices connected to the PVS"""
        return self.generic_command("DeviceList")

    def network_status(self):
        """Get a list of network interfaces on the PVS"""
        return self.generic_command("Get_Comm")
