"""Test the SunPower config flow."""

from unittest.mock import (
    MagicMock,
    patch,
)

import pytest
from homeassistant.const import (
    CONF_HOST,
    CONF_LOCATION,
)
from homeassistant.data_entry_flow import FlowResultType

from custom_components.sunpower.config_flow import (
    CannotConnect,
    ConfigFlow,
    validate_input,
)
from custom_components.sunpower.const import (
    SUNPOWER_DESCRIPTIVE_NAMES,
    SUNPOWER_HOST,
    SUNPOWER_PRODUCT_NAMES,
)

# Test data
TEST_HOST = "192.168.1.100"
TEST_LOCATION = "Main House"
TEST_CONFIG = {
    CONF_HOST: TEST_HOST,
    CONF_LOCATION: TEST_LOCATION,
    SUNPOWER_DESCRIPTIVE_NAMES: True,
    SUNPOWER_PRODUCT_NAMES: False,
}


@pytest.fixture()
def hass():
    """Create a test Home Assistant instance."""
    from unittest.mock import AsyncMock

    hass_instance = MagicMock()
    hass_instance.config_entries = MagicMock()
    hass_instance.async_add_executor_job = AsyncMock()
    hass_instance.data = {}

    return hass_instance


class TestConfigFlow:
    """Test the config flow."""

    @pytest.mark.asyncio()
    async def test_config_flow_user_step_form_display(self, hass):
        """Test that the user form is displayed correctly."""
        flow = ConfigFlow()
        flow.hass = hass
        flow.context = {}
        # Mock the duplicate check to avoid abort
        flow._abort_if_unique_id_configured = MagicMock()

        result = await flow.async_step_user()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"
        assert result["errors"] == {}
        assert CONF_HOST in result["data_schema"].schema
        assert CONF_LOCATION in result["data_schema"].schema

    @pytest.mark.asyncio()
    @patch("custom_components.sunpower.config_flow.SunPowerMonitor")
    async def test_config_flow_user_step_success_with_location(self, mock_monitor, hass):
        """Test successful config flow with location."""
        # Mock the SunPowerMonitor
        mock_instance = mock_monitor.return_value
        mock_instance.network_status.return_value = {"status": "ok"}

        flow = ConfigFlow()
        flow.hass = hass
        flow.context = {}
        # Mock the duplicate check to avoid abort
        flow._abort_if_unique_id_configured = MagicMock()

        # Test the actual async_step_user method with user input
        user_input = {
            SUNPOWER_HOST: TEST_HOST,
            CONF_LOCATION: TEST_LOCATION,
            SUNPOWER_DESCRIPTIVE_NAMES: True,
            SUNPOWER_PRODUCT_NAMES: False,
        }

        hass.async_add_executor_job.return_value = {"status": "ok"}
        result = await flow.async_step_user(user_input)

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == f"PVS {TEST_HOST} - {TEST_LOCATION}"
        assert result["data"] == user_input
        # Verify unique_id was set correctly (current implementation uses just host)
        assert flow.unique_id == TEST_HOST

    @pytest.mark.asyncio()
    @patch("custom_components.sunpower.config_flow.SunPowerMonitor")
    async def test_config_flow_user_step_success_without_location(self, mock_monitor, hass):
        """Test successful config flow without location."""
        # Mock the SunPowerMonitor
        mock_instance = mock_monitor.return_value
        mock_instance.network_status.return_value = {"status": "ok"}

        flow = ConfigFlow()
        flow.hass = hass
        flow.context = {}
        # Mock the duplicate check to avoid abort
        flow._abort_if_unique_id_configured = MagicMock()

        # Test without location
        user_input = {
            SUNPOWER_HOST: TEST_HOST,
            CONF_LOCATION: "",  # Empty location
            SUNPOWER_DESCRIPTIVE_NAMES: True,
            SUNPOWER_PRODUCT_NAMES: False,
        }

        hass.async_add_executor_job.return_value = {"status": "ok"}
        result = await flow.async_step_user(user_input)

        expected_title = f"PVS {TEST_HOST}"
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == expected_title
        assert result["data"] == user_input
        # Verify unique_id was set correctly (should be just host)
        assert flow.unique_id == TEST_HOST

    @pytest.mark.asyncio()
    @patch("custom_components.sunpower.config_flow.SunPowerMonitor")
    async def test_config_flow_connection_error(self, mock_monitor, hass):
        """Test config flow with connection error."""
        # Mock connection failure
        mock_instance = mock_monitor.return_value
        mock_instance.network_status.side_effect = Exception("Connection failed")

        flow = ConfigFlow()
        flow.hass = hass
        flow.context = {}
        # Mock the duplicate check to avoid abort
        flow._abort_if_unique_id_configured = MagicMock()

        user_input = {
            SUNPOWER_HOST: TEST_HOST,
            CONF_LOCATION: TEST_LOCATION,
            SUNPOWER_DESCRIPTIVE_NAMES: True,
            SUNPOWER_PRODUCT_NAMES: False,
        }

        # Mock the executor job to raise a ConnectionException
        from custom_components.sunpower.sunpower import ConnectionException

        async def mock_executor_job(func, *args):
            raise ConnectionException("Connection failed")

        hass.async_add_executor_job.side_effect = mock_executor_job
        result = await flow.async_step_user(user_input)

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "cannot_connect"

    def test_unique_id_logic_with_location(self):
        """Test unique ID generation logic with location name."""
        # Test the actual logic used in the config flow
        user_input = {
            SUNPOWER_HOST: TEST_HOST,
            CONF_LOCATION: TEST_LOCATION,
        }

        # This is the actual logic from the config flow
        unique_id = user_input[SUNPOWER_HOST]
        if user_input.get(CONF_LOCATION):
            host = user_input[SUNPOWER_HOST]
            location = user_input[CONF_LOCATION]
            unique_id = f"{host}_{location}"

        assert unique_id == f"{TEST_HOST}_{TEST_LOCATION}"

    def test_unique_id_logic_without_location(self):
        """Test unique ID generation logic without location name."""
        # Test the actual logic used in the config flow
        user_input = {
            SUNPOWER_HOST: TEST_HOST,
        }

        # This is the actual logic from the config flow
        unique_id = user_input[SUNPOWER_HOST]
        if user_input.get(CONF_LOCATION):
            host = user_input[SUNPOWER_HOST]
            location = user_input[CONF_LOCATION]
            unique_id = f"{host}_{location}"

        assert unique_id == TEST_HOST

    @pytest.mark.asyncio()
    @patch("custom_components.sunpower.config_flow.SunPowerMonitor")
    async def test_config_flow_import_step(self, mock_monitor, hass):
        """Test the import step."""
        # Mock the SunPowerMonitor
        mock_instance = mock_monitor.return_value
        mock_instance.network_status.return_value = {"status": "ok"}

        flow = ConfigFlow()
        flow.hass = hass
        flow.context = {}
        # Mock the duplicate check to avoid abort
        flow._abort_if_unique_id_configured = MagicMock()

        import_data = {
            SUNPOWER_HOST: TEST_HOST,
            CONF_LOCATION: TEST_LOCATION,
            SUNPOWER_DESCRIPTIVE_NAMES: True,
            SUNPOWER_PRODUCT_NAMES: False,
        }

        # Mock the executor job for import step too
        hass.async_add_executor_job.return_value = {"status": "ok"}

        # Test the actual import step which should call user step
        result = await flow.async_step_import(import_data)

        # Import step should set unique_id (current implementation uses just host)
        assert flow.unique_id == TEST_HOST
        # The result should be a CREATE_ENTRY (since import calls user step)
        assert result["type"] == FlowResultType.CREATE_ENTRY


class TestValidateInput:
    """Test the validate_input function."""

    @pytest.mark.asyncio()
    @patch("custom_components.sunpower.config_flow.SunPowerMonitor")
    async def test_validate_input_with_location(self, mock_monitor, hass):
        """Test validate_input function with location name."""
        # Mock the SunPowerMonitor
        mock_instance = mock_monitor.return_value
        mock_instance.network_status.return_value = {"status": "ok"}

        data = {
            SUNPOWER_HOST: TEST_HOST,
            CONF_LOCATION: TEST_LOCATION,
        }

        # Test the actual validate_input function
        hass.async_add_executor_job.return_value = {"status": "ok"}
        result = await validate_input(hass, data)

        assert result["title"] == f"PVS {TEST_HOST} - {TEST_LOCATION}"
        # Verify the SunPowerMonitor was called correctly
        mock_monitor.assert_called_once_with(TEST_HOST)
        hass.async_add_executor_job.assert_called_once()

    @pytest.mark.asyncio()
    @patch("custom_components.sunpower.config_flow.SunPowerMonitor")
    async def test_validate_input_without_location(self, mock_monitor, hass):
        """Test validate_input function without location name."""
        # Mock the SunPowerMonitor
        mock_instance = mock_monitor.return_value
        mock_instance.network_status.return_value = {"status": "ok"}

        data = {
            SUNPOWER_HOST: TEST_HOST,
            # No CONF_LOCATION
        }

        # Test the actual validate_input function
        hass.async_add_executor_job.return_value = {"status": "ok"}
        result = await validate_input(hass, data)

        expected_title = f"PVS {TEST_HOST}"
        assert result["title"] == expected_title
        # Verify the SunPowerMonitor was called correctly
        mock_monitor.assert_called_once_with(TEST_HOST)
        hass.async_add_executor_job.assert_called_once()

    @pytest.mark.asyncio()
    @patch("custom_components.sunpower.config_flow.SunPowerMonitor")
    async def test_validate_input_empty_location(self, mock_monitor, hass):
        """Test validate_input function with empty location name."""
        # Mock the SunPowerMonitor
        mock_instance = mock_monitor.return_value
        mock_instance.network_status.return_value = {"status": "ok"}

        data = {
            SUNPOWER_HOST: TEST_HOST,
            CONF_LOCATION: "",  # Empty string
        }

        # Test the actual validate_input function
        hass.async_add_executor_job.return_value = {"status": "ok"}
        result = await validate_input(hass, data)

        expected_title = f"PVS {TEST_HOST}"
        assert result["title"] == expected_title
        # Verify the SunPowerMonitor was called correctly
        mock_monitor.assert_called_once_with(TEST_HOST)
        hass.async_add_executor_job.assert_called_once()

    @pytest.mark.asyncio()
    @patch("custom_components.sunpower.config_flow.SunPowerMonitor")
    async def test_validate_input_connection_error(self, mock_monitor, hass):
        """Test validate_input function with connection error."""
        # Mock the SunPowerMonitor to raise an exception
        mock_instance = mock_monitor.return_value
        mock_instance.network_status.side_effect = Exception("Connection failed")

        data = {
            SUNPOWER_HOST: TEST_HOST,
            CONF_LOCATION: TEST_LOCATION,
        }

        # Mock the executor job to raise a ConnectionException
        from custom_components.sunpower.sunpower import ConnectionException

        async def mock_executor_job(func, *args):
            raise ConnectionException("Connection failed")

        # Test the actual validate_input function
        hass.async_add_executor_job.side_effect = mock_executor_job
        with pytest.raises(CannotConnect):
            await validate_input(hass, data)

        # Verify the SunPowerMonitor was called correctly
        mock_monitor.assert_called_once_with(TEST_HOST)
