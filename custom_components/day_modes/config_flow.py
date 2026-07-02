"""Config flow for Day modes integration."""

from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_ZONE,
    DEFAULT_MORNING_TIME,
    DEFAULT_DAY_TIME,
    DEFAULT_EVENING_TIME,
    DEFAULT_NIGHT_TIME,
    CONF_HOME_ZONE,
    CONF_MORNING_TIME,
    CONF_DAY_TIME,
    CONF_EVENING_TIME,
    CONF_NIGHT_TIME,
)


def get_schema(defaults: dict[str, Any]) -> vol.Schema:
    """Return the configuration schema using clean text inputs for time."""
    return vol.Schema(
        {
            vol.Required(
                CONF_HOME_ZONE, default=defaults.get(CONF_HOME_ZONE, DEFAULT_ZONE)
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="zone")),
            vol.Required(
                CONF_MORNING_TIME,
                default=defaults.get(CONF_MORNING_TIME, DEFAULT_MORNING_TIME),
            ): selector.TextSelector(),
            vol.Required(
                CONF_DAY_TIME, default=defaults.get(CONF_DAY_TIME, DEFAULT_DAY_TIME)
            ): selector.TextSelector(),
            vol.Required(
                CONF_EVENING_TIME,
                default=defaults.get(CONF_EVENING_TIME, DEFAULT_EVENING_TIME),
            ): selector.TextSelector(),
            vol.Required(
                CONF_NIGHT_TIME,
                default=defaults.get(CONF_NIGHT_TIME, DEFAULT_NIGHT_TIME),
            ): selector.TextSelector(),
        }
    )


class DayModesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Day modes."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            title = f"{DEFAULT_NAME} ({user_input[CONF_HOME_ZONE].split('.')[-1].title()})"
            return self.async_create_entry(
                title=title, data=user_input, options=user_input
            )

        return self.async_show_form(
            step_id="user", data_schema=get_schema({}), errors=errors
        )

    @callback
    def async_get_options_flow(
        self, config_entry: config_entries.ConfigEntry
    ) -> DayModesOptionsFlowHandler:
        """Get the options flow for this handler."""
        return DayModesOptionsFlowHandler()


class DayModesOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow changes for reconfiguration."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Access current settings through the inherited config_entry property
        current_settings = {**self.config_entry.data, **self.config_entry.options}

        return self.async_show_form(
            step_id="init", data_schema=get_schema(current_settings)
        )
