"""Config flow for sunpower integration."""

import logging

import voluptuous as vol
from homeassistant import (
    config_entries,
    core,
    exceptions,
)
from homeassistant.const import CONF_HOST

from .const import (
    DEFAULT_SUNPOWER_UPDATE_INTERVAL,
    DEFAULT_SUNVAULT_UPDATE_INTERVAL,
    DOMAIN,
    MIN_SUNPOWER_UPDATE_INTERVAL,
    MIN_SUNVAULT_UPDATE_INTERVAL,
    SUNPOWER_DESCRIPTIVE_NAMES,
    SUNPOWER_HOST,
    SUNPOWER_PRODUCT_NAMES,
    SUNPOWER_UPDATE_INTERVAL,
    SUNVAULT_UPDATE_INTERVAL,
)
from .sunpower import (
    ConnectionException,
    SunPowerMonitor,
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(SUNPOWER_DESCRIPTIVE_NAMES, default=True): bool,
        vol.Required(SUNPOWER_PRODUCT_NAMES, default=False): bool,
    },
)


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """

    spm = SunPowerMonitor(data[SUNPOWER_HOST])
    name = "PVS {}".format(data[SUNPOWER_HOST])
    try:
        response = await hass.async_add_executor_job(spm.network_status)
        _LOGGER.debug("Got from %s %s", data[SUNPOWER_HOST], response)
    except ConnectionException as error:
        raise CannotConnect from error

    return {"title": name}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for sunpower."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    @staticmethod
    @core.callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input: dict[str, any] | None = None):
        """Handle the initial step."""
        errors = {}
        if user_input:
            _LOGGER.debug(f"User Setup: host={user_input.get(CONF_HOST)}")
        else:
            _LOGGER.debug("User Setup: initial form display")
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                await self.async_set_unique_id(user_input[SUNPOWER_HOST])
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidHost:
                errors["base"] = "invalid_host"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_import(self, user_input: dict[str, any] | None = None):
        """Handle import."""
        await self.async_set_unique_id(user_input[SUNPOWER_HOST])
        self._abort_if_unique_id_configured()
        return await self.async_step_user(user_input)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, any] | None = None,
    ) -> config_entries.FlowResult:
        """Manage the options."""
        if user_input:
            _LOGGER.debug(f"Options input: intervals={user_input.get(SUNPOWER_UPDATE_INTERVAL)}/{user_input.get(SUNVAULT_UPDATE_INTERVAL)}")
        else:
            _LOGGER.debug("Options: initial form display")
        options = dict(self.config_entry.options)

        errors = {}

        if user_input is not None:
            if user_input[SUNPOWER_UPDATE_INTERVAL] < MIN_SUNPOWER_UPDATE_INTERVAL:
                errors[SUNPOWER_UPDATE_INTERVAL] = "MIN_INTERVAL"
            if user_input[SUNVAULT_UPDATE_INTERVAL] < MIN_SUNVAULT_UPDATE_INTERVAL:
                errors[SUNPOWER_UPDATE_INTERVAL] = "MIN_INTERVAL"
            if len(errors) == 0:
                options[SUNPOWER_UPDATE_INTERVAL] = user_input[SUNPOWER_UPDATE_INTERVAL]
                options[SUNVAULT_UPDATE_INTERVAL] = user_input[SUNVAULT_UPDATE_INTERVAL]
                return self.async_create_entry(title="", data=user_input)

        current_sunpower_interval = options.get(
            SUNPOWER_UPDATE_INTERVAL,
            DEFAULT_SUNPOWER_UPDATE_INTERVAL,
        )
        current_sunvault_interval = options.get(
            SUNVAULT_UPDATE_INTERVAL,
            DEFAULT_SUNVAULT_UPDATE_INTERVAL,
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(SUNPOWER_UPDATE_INTERVAL, default=current_sunpower_interval): int,
                    vol.Required(SUNVAULT_UPDATE_INTERVAL, default=current_sunvault_interval): int,
                },
            ),
            errors=errors,
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
