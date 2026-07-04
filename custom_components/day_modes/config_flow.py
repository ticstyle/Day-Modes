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
)

WEEKDAYS_EN = {
    "monday": "Monday",
    "tuesday": "Tuesday",
    "wednesday": "Wednesday",
    "thursday": "Thursday",
    "friday": "Friday",
    "saturday": "Saturday",
    "sunday": "Sunday",
}

WEEKDAYS_SV = {
    "monday": "Måndag",
    "tuesday": "Tisdag",
    "wednesday": "Onsdag",
    "thursday": "Torsdag",
    "friday": "Fredag",
    "saturday": "Lördag",
    "sunday": "Söndag",
}


def get_time_schema(defaults: dict[str, Any]) -> dict[vol.Marker, Any]:
    """Return the baseline time selectors populated with accurate defaults."""
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
            CONF_NIGHT_TIME,
            default=defaults.get(CONF_NIGHT_TIME, DEFAULT_NIGHT_TIME),
        ): selector.TextSelector(),
    }


class DayModesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a multi-step dynamic config flow for Day modes."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the multi-step wizard properties using day strings."""
        self._schedules: list[dict[str, Any]] = []
        self._remaining_days: list[str] = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        self._home_zone: str = DEFAULT_ZONE

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: Configure home zone, default schedule, and select initial days."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._home_zone = user_input[CONF_HOME_ZONE]
            chosen_days = user_input.get("days", [])

            checked_days = [d for d in self._remaining_days if d in chosen_days]
            unchecked_days = [d for d in self._remaining_days if d not in chosen_days]

            if not checked_days:
                errors["base"] = "select_at_least_one_day"
            else:
                self._schedules.append(
                    {
                        "days": checked_days,
                        CONF_MORNING_TIME: user_input[CONF_MORNING_TIME],
                        CONF_DAY_TIME: user_input[CONF_DAY_TIME],
                        CONF_EVENING_TIME: user_input[CONF_EVENING_TIME],
                        CONF_NIGHT_TIME: user_input[CONF_NIGHT_TIME],
                    }
                )
                self._remaining_days = unchecked_days

                if not self._remaining_days:
                    return self.async_create_entry(
                        title=f"{DEFAULT_NAME} ({self._home_zone.split('.')[-1].title()})",
                        data={
                            CONF_HOME_ZONE: self._home_zone,
                            CONF_SCHEDULES: self._schedules,
                        },
                        options={
                            CONF_HOME_ZONE: self._home_zone,
                            CONF_SCHEDULES: self._schedules,
                        },
                    )
                return await self.async_step_special()

        schema_dict = {
            vol.Required(
                CONF_HOME_ZONE, default=self._home_zone
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="zone"))
        }
        schema_dict.update(get_time_schema({}))

        # Plain list of string values makes the checkbox list perfectly stable
        schema_dict[vol.Required("days", default=list(self._remaining_days))] = (
            selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(self._remaining_days),
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                )
            )
        )

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(schema_dict), errors=errors
        )

    async def async_step_special(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2 & onwards: Recursively isolate remaining weekdays including the final day."""
        errors: dict[str, str] = {}
        lang = "sv" if self.hass.config.language == "sv" else "en"
        day_map = WEEKDAYS_SV if lang == "sv" else WEEKDAYS_EN

        if user_input is not None:
            chosen_days = user_input.get("days", [])
            checked_days = [d for d in self._remaining_days if d in chosen_days]
            unchecked_days = [d for d in self._remaining_days if d not in chosen_days]

            if not checked_days:
                errors["base"] = "select_at_least_one_day"
            else:
                self._schedules.append(
                    {
                        "days": checked_days,
                        CONF_MORNING_TIME: user_input[CONF_MORNING_TIME],
                        CONF_DAY_TIME: user_input[CONF_DAY_TIME],
                        CONF_EVENING_TIME: user_input[CONF_EVENING_TIME],
                        CONF_NIGHT_TIME: user_input[CONF_NIGHT_TIME],
                    }
                )
                self._remaining_days = unchecked_days

                if not self._remaining_days:
                    return self.async_create_entry(
                        title=f"{DEFAULT_NAME} ({self._home_zone.split('.')[-1].title()})",
                        data={
                            CONF_HOME_ZONE: self._home_zone,
                            CONF_SCHEDULES: self._schedules,
                        },
                        options={
                            CONF_HOME_ZONE: self._home_zone,
                            CONF_SCHEDULES: self._schedules,
                        },
                    )
                return await self.async_step_special()

        schema_dict = get_time_schema({})
        schema_dict[vol.Required("days", default=list(self._remaining_days))] = (
            selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(self._remaining_days),
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                )
            )
        )

        remaining_days_str = ", ".join([day_map[d] for d in self._remaining_days])

        return self.async_show_form(
            step_id="special",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={"remaining_days": remaining_days_str},
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
    """Handle options flow changes extracting active historical datasets."""

    def __init__(self) -> None:
        """Initialize options multi-step state trackers."""
        self._schedules: list[dict[str, Any]] = []
        self._remaining_days: list[str] = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        self._step_index = 0
        self._home_zone = DEFAULT_ZONE

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Initialize the reconfiguration wizard populating stored matrixes."""
        errors: dict[str, str] = {}
        current_config = {**self.config_entry.data, **self.config_entry.options}
        self._home_zone = current_config.get(CONF_HOME_ZONE, DEFAULT_ZONE)
        saved_schedules = current_config.get(CONF_SCHEDULES, [])

        if user_input is not None:
            self._home_zone = user_input[CONF_HOME_ZONE]
            chosen_days = user_input.get("days", [])

            checked_days = [d for d in self._remaining_days if d in chosen_days]
            unchecked_days = [d for d in self._remaining_days if d not in chosen_days]

            if not checked_days:
                errors["base"] = "select_at_least_one_day"
            else:
                self._schedules.append(
                    {
                        "days": checked_days,
                        CONF_MORNING_TIME: user_input[CONF_MORNING_TIME],
                        CONF_DAY_TIME: user_input[CONF_DAY_TIME],
                        CONF_EVENING_TIME: user_input[CONF_EVENING_TIME],
                        CONF_NIGHT_TIME: user_input[CONF_NIGHT_TIME],
                    }
                )
                self._remaining_days = unchecked_days
                self._step_index += 1

                if not self._remaining_days:
                    return self.async_create_entry(
                        title="",
                        data={
                            CONF_HOME_ZONE: self._home_zone,
                            CONF_SCHEDULES: self._schedules,
                        },
                    )
                return await self.async_step_special()

        defaults = {CONF_HOME_ZONE: self._home_zone}
        default_days = []

        if saved_schedules and len(saved_schedules) > self._step_index:
            active_profile = saved_schedules[self._step_index]
            defaults.update(
                {
                    CONF_MORNING_TIME: active_profile.get(CONF_MORNING_TIME),
                    CONF_DAY_TIME: active_profile.get(CONF_DAY_TIME),
                    CONF_EVENING_TIME: active_profile.get(CONF_EVENING_TIME),
                    CONF_NIGHT_TIME: active_profile.get(CONF_NIGHT_TIME),
                }
            )
            default_days = [
                d for d in self._remaining_days if d in active_profile.get("days", [])
            ]
        else:
            default_days = list(self._remaining_days)

        schema_dict = {
            vol.Required(
                CONF_HOME_ZONE, default=defaults[CONF_HOME_ZONE]
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="zone"))
        }
        schema_dict.update(get_time_schema(defaults))
        schema_dict[vol.Required("days", default=default_days)] = (
            selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(self._remaining_days),
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                )
            )
        )

        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(schema_dict), errors=errors
        )

    async def async_step_special(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Recursively process remaining days maintaining option constraints."""
        errors: dict[str, str] = {}
        current_config = {**self.config_entry.data, **self.config_entry.options}
        saved_schedules = current_config.get(CONF_SCHEDULES, [])
        lang = "sv" if self.hass.config.language == "sv" else "en"
        day_map = WEEKDAYS_SV if lang == "sv" else WEEKDAYS_EN

        if user_input is not None:
            chosen_days = user_input.get("days", [])
            checked_days = [d for d in self._remaining_days if d in chosen_days]
            unchecked_days = [d for d in self._remaining_days if d not in chosen_days]

            if not checked_days:
                errors["base"] = "select_at_least_one_day"
            else:
                self._schedules.append(
                    {
                        "days": checked_days,
                        CONF_MORNING_TIME: user_input[CONF_MORNING_TIME],
                        CONF_DAY_TIME: user_input[CONF_DAY_TIME],
                        CONF_EVENING_TIME: user_input[CONF_EVENING_TIME],
                        CONF_NIGHT_TIME: user_input[CONF_NIGHT_TIME],
                    }
                )
                self._remaining_days = unchecked_days
                self._step_index += 1

                if not self._remaining_days:
                    return self.async_create_entry(
                        title="",
                        data={
                            CONF_HOME_ZONE: self._home_zone,
                            CONF_SCHEDULES: self._schedules,
                        },
                    )
                return await self.async_step_special()

        defaults = {}
        default_days = []

        if saved_schedules and len(saved_schedules) > self._step_index:
            active_profile = saved_schedules[self._step_index]
            defaults.update(
                {
                    CONF_MORNING_TIME: active_profile.get(CONF_MORNING_TIME),
                    CONF_DAY_TIME: active_profile.get(CONF_DAY_TIME),
                    CONF_EVENING_TIME: active_profile.get(CONF_EVENING_TIME),
                    CONF_NIGHT_TIME: active_profile.get(CONF_NIGHT_TIME),
                }
            )
            default_days = [
                d for d in self._remaining_days if d in active_profile.get("days", [])
            ]
        else:
            default_days = list(self._remaining_days)

        schema_dict = get_time_schema(defaults)
        schema_dict[vol.Required("days", default=default_days)] = (
            selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(self._remaining_days),
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                )
            )
        )

        remaining_days_str = ", ".join([day_map[d] for d in self._remaining_days])

        return self.async_show_form(
            step_id="special",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={"remaining_days": remaining_days_str},
            errors=errors,
        )
