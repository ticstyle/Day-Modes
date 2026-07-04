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
    CONF_SCHEDULES,
    WEEKDAYS,
)


def get_time_schema(defaults: dict[str, Any]) -> dict[vol.Marker, Any]:
    """Return the baseline time selectors used across all wizard steps."""
    return {
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
            CONF_NIGHT_TIME, default=defaults.get(CONF_NIGHT_TIME, DEFAULT_NIGHT_TIME)
        ): selector.TextSelector(),
    }


class DayModesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a multi-step dynamic config flow for Day modes."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the multi-step wizard properties."""
        self._schedules: list[dict[str, Any]] = []
        self._remaining_days: list[int] = [0, 1, 2, 3, 4, 5, 6]
        self._home_zone: str = DEFAULT_ZONE

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: Configure home zone, default schedule, and select initial days."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._home_zone = user_input[CONF_HOME_ZONE]

            # Separate chosen days from deferred days
            checked_days = [d for d in self._remaining_days if user_input.get(f"day_{d}", False)]
            unchecked_days = [d for d in self._remaining_days if not user_input.get(f"day_{d}", False)]

            if not checked_days:
                errors["base"] = "select_at_least_one_day"
            else:
                self._schedules.append({
                    "days": checked_days,
                    CONF_MORNING_TIME: user_input[CONF_MORNING_TIME],
                    CONF_DAY_TIME: user_input[CONF_DAY_TIME],
                    CONF_EVENING_TIME: user_input[CONF_EVENING_TIME],
                    CONF_NIGHT_TIME: user_input[CONF_NIGHT_TIME],
                })
                self._remaining_days = unchecked_days

                if not self._remaining_days:
                    return self.async_create_entry(
                        title=f"{DEFAULT_NAME} ({self._home_zone.split('.')[-1].title()})",
                        data={CONF_HOME_ZONE: self._home_zone, CONF_SCHEDULES: self._schedules},
                        options={CONF_HOME_ZONE: self._home_zone, CONF_SCHEDULES: self._schedules},
                    )
                return await self.async_step_special()

        # Build schema showing all 7 days as default checked boxes
        schema_dict = {
            vol.Required(CONF_HOME_ZONE, default=self._home_zone): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="zone")
            )
        }
        schema_dict.update(get_time_schema({}))
        for d in self._remaining_days:
            schema_dict[vol.Required(f"day_{d}", default=True)] = selector.BooleanSelector()

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(schema_dict), errors=errors
        )

    async def async_step_special(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2 & onwards: Recursively isolate remaining unconfigured weekdays."""
        errors: dict[str, str] = {}
        total_left = len(self._remaining_days)

        if user_input is not None:
            if total_left == 1:
                checked_days = list(self._remaining_days)
                unchecked_days = []
            else:
                checked_days = [d for d in self._remaining_days if user_input.get(f"day_{d}", False)]
                unchecked_days = [d for d in self._remaining_days if not user_input.get(f"day_{d}", False)]

            if not checked_days:
                errors["base"] = "select_at_least_one_day"
            else:
                self._schedules.append({
                    "days": checked_days,
                    CONF_MORNING_TIME: user_input[CONF_MORNING_TIME],
                    CONF_DAY_TIME: user_input[CONF_DAY_TIME],
                    CONF_EVENING_TIME: user_input[CONF_EVENING_TIME],
                    CONF_NIGHT_TIME: user_input[CONF_NIGHT_TIME],
                })
                self._remaining_days = unchecked_days

                if not self._remaining_days:
                    return self.async_create_entry(
                        title=f"{DEFAULT_NAME} ({self._home_zone.split('.')[-1].title()})",
                        data={CONF_HOME_ZONE: self._home_zone, CONF_SCHEDULES: self._schedules},
                        options={CONF_HOME_ZONE: self._home_zone, CONF_SCHEDULES: self._schedules},
                    )
                return await self.async_step_special()

        # Generate schema tailored only to what days are left
        schema_dict = get_time_schema({})
        if total_left > 1:
            for d in self._remaining_days:
                schema_dict[vol.Required(f"day_{d}", default=True)] = selector.BooleanSelector()

        # Compile dynamic lists for frontend UI translation placeholders
        day_names = [f"{{{{day_{d}}}}}" for d in self._remaining_days]
        placeholders = {"days": ", ".join(day_names)}

        return self.async_show_form(
            step_id="special",
            data_schema=vol.Schema(schema_dict),
            description_placeholders=placeholders,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> DayModesOptionsFlowHandler:
        """Get the options flow for this handler."""
        return DayModesOptionsFlowHandler()


class DayModesOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow changes mirroring the main dynamic setup logic."""

    def __init__(self) -> None:
        """Initialize options multi-step state trackers."""
        self._schedules: list[dict[str, Any]] = []
        self._remaining_days: list[int] = [0, 1, 2, 3, 4, 5, 6]

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Initialize the reconfiguration wizard."""
        errors: dict[str, str] = {}
        current_zone = self.config_entry.options.get(
            CONF_HOME_ZONE, self.config_entry.data.get(CONF_HOME_ZONE, DEFAULT_ZONE)
        )

        if user_input is not None:
            self._home_zone = user_input[CONF_HOME_ZONE]
            checked_days = [d for d in self._remaining_days if user_input.get(f"day_{d}", False)]
            unchecked_days = [d for d in self._remaining_days if not user_input.get(f"day_{d}", False)]

            if not checked_days:
                errors["base"] = "select_at_least_one_day"
            else:
                self._schedules.append({
                    "days": checked_days,
                    CONF_MORNING_TIME: user_input[CONF_MORNING_TIME],
                    CONF_DAY_TIME: user_input[CONF_DAY_TIME],
                    CONF_EVENING_TIME: user_input[CONF_EVENING_TIME],
                    CONF_NIGHT_TIME: user_input[CONF_NIGHT_TIME],
                })
                self._remaining_days = unchecked_days

                if not self._remaining_days:
                    return self.async_create_entry(
                        title="",
                        data={CONF_HOME_ZONE: self._home_zone, CONF_SCHEDULES: self._schedules},
                    )
                return await self.async_step_special()

        schema_dict = {
            vol.Required(CONF_HOME_ZONE, default=current_zone): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="zone")
            )
        }
        schema_dict.update(get_time_schema({}))
        for d in self._remaining_days:
            schema_dict[vol.Required(f"day_{d}", default=True)] = selector.BooleanSelector()

        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(schema_dict), errors=errors
        )

    async def async_step_special(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Recursively gather options data for unassigned days during reconfiguration."""
        errors: dict[str, str] = {}
        total_left = len(self._remaining_days)

        if user_input is not None:
            if total_left == 1:
                checked_days = list(self._remaining_days)
                unchecked_days = []
            else:
                checked_days = [d for d in self._remaining_days if user_input.get(f"day_{d}", False)]
                unchecked_days = [d for d in self._remaining_days if not user_input.get(f"day_{d}", False)]

            if not checked_days:
                errors["base"] = "select_at_least_one_day"
            else:
                self._schedules.append({
                    "days": checked_days,
                    CONF_MORNING_TIME: user_input[CONF_MORNING_TIME],
                    CONF_DAY_TIME: user_input[CONF_DAY_TIME],
                    CONF_EVENING_TIME: user_input[CONF_EVENING_TIME],
                    CONF_NIGHT_TIME: user_input[CONF_NIGHT_TIME],
                })
                self._remaining_days = unchecked_days

                if not self._remaining_days:
                    return self.async_create_entry(
                        title="",
                        data={CONF_HOME_ZONE: self._home_zone, CONF_SCHEDULES: self._schedules},
                    )
                return await self.async_step_special()

        schema_dict = get_time_schema({})
        if total_left > 1:
            for d in self._remaining_days:
                schema_dict[vol.Required(f"day_{d}", default=True)] = selector.BooleanSelector()

        day_names = [f"{{{{day_{d}}}}}" for d in self._remaining_days]
        placeholders = {"days": ", ".join(day_names)}

        return self.async_show_form(
            step_id="special",
            data_schema=vol.Schema(schema_dict),
            description_placeholders=placeholders,
            errors=errors,
        )
