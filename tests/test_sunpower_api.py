"""Test the SunPower API client."""

import os
import sys
from unittest.mock import (
    Mock,
    patch,
)

import pytest
import requests

# Add custom_components to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

from sunpower.sunpower import (  # noqa: E402
    ConnectionException,
    SunPowerMonitor,
)


class TestSunPowerMonitor:
    """Test the SunPowerMonitor class."""

    def test_init(self):
        """Test SunPowerMonitor initialization."""
        monitor = SunPowerMonitor("192.168.1.100")
        assert monitor.host == "192.168.1.100"
        assert monitor.command_url == "http://192.168.1.100/cgi-bin/dl_cgi?Command="

    @patch("sunpower.sunpower.requests")
    def test_device_list_success(self, mock_requests):
        """Test successful device list retrieval."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"devices": []}
        mock_requests.get.return_value = mock_response

        monitor = SunPowerMonitor("192.168.1.100")
        result = monitor.device_list()

        assert result == {"devices": []}
        mock_requests.get.assert_called_once_with(
            "http://192.168.1.100/cgi-bin/dl_cgi?Command=DeviceList",
            timeout=120,
        )

    @patch("sunpower.sunpower.requests")
    def test_device_list_connection_error(self, mock_requests):
        """Test device list with connection error."""
        # Mock the exception class as well
        mock_requests.exceptions.RequestException = requests.exceptions.RequestException
        mock_requests.get.side_effect = requests.exceptions.RequestException("Connection failed")

        monitor = SunPowerMonitor("192.168.1.100")

        with pytest.raises(ConnectionException):
            monitor.device_list()

    @patch("sunpower.sunpower.requests")
    def test_network_status_success(self, mock_requests):
        """Test successful network status retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response

        monitor = SunPowerMonitor("192.168.1.100")
        result = monitor.network_status()

        assert result == {"status": "ok"}
        mock_requests.get.assert_called_once_with(
            "http://192.168.1.100/cgi-bin/dl_cgi?Command=Get_Comm",
            timeout=120,
        )
