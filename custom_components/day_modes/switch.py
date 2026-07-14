"""Platform for switch integration."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
import homeassistant.util.dt as dt_util

from .const import CONF_VACATION_CALENDAR, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Day modes switch platform."""
    config = {**config_entry.data, **config_entry.options}

    device_info = DeviceInfo(
        identifiers={(DOMAIN, config_entry.entry_id)},
        name="Day modes",
        manufacturer="ticstyle",
        model="Day Modes",
    )

    async_add_entities(
        [DayModesVacationSwitch(config_entry, config, device_info)],
        update_before_add=True,
    )


class DayModesVacationSwitch(SwitchEntity):
    """Representation of the Vacation Mode Switch with automated daily calendar tracking."""

    _attr_icon = "mdi:airplane"
    _attr_has_entity_name = True
    _attr_translation_key = "vacation_mode"

    def __init__(
        self, config_entry: ConfigEntry, config: dict[str, Any], device_info: DeviceInfo
    ) -> None:
        """Initialize the switch."""
        self._config_entry = config_entry
        self._config = config
        self._attr_device_info = device_info
        self._attr_unique_id = f"{config_entry.entry_id}_vacation_mode"
        self._attr_name = "Vacation mode"
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        """Set up daily calendar check at startup and scheduled times."""
        calendar_entity = self._config.get(CONF_VACATION_CALENDAR)
        if not calendar_entity:
            return

        # Run scheduled daily checks 47 seconds after midnight to reduce system loads
        self.async_on_remove(
            async_track_time_change(
                self.hass,
                self._async_scheduled_update,
                hour=0,
                minute=0,
                second=47,
            )
        )

        # Perform an initial update on startup
        await self._async_update_from_calendar()

    @callback
    def _async_scheduled_update(self, now: datetime) -> None:
        """Handle scheduled trigger by creating an async task."""
        self.hass.async_create_task(self._async_update_from_calendar())

    async def _async_update_from_calendar(self) -> None:
        """Query the calendar and update state based on today's events."""
        calendar_entity = self._config.get(CONF_VACATION_CALENDAR)
        if not calendar_entity:
            return

        now = dt_util.now()
        start = dt_util.start_of_local_day(now)
        end = start + timedelta(days=1)

        try:
            # Fetch events using the official service call API to avoid breaking internal dependency changes
            response = await self.hass.services.async_call(
                "calendar",
                "get_events",
                {
                    "entity_id": calendar_entity,
                    "start_date_time": start.isoformat(),
                    "end_date_time": end.isoformat(),
                },
                blocking=True,
                return_response=True,
            )

            # Safely check if we got a valid response and verify today's event list
            if response and isinstance(response, dict):
                calendar_data = response.get(calendar_entity, {})
                events = calendar_data.get("events", [])
                self._attr_is_on = len(events) > 0
            else:
                _LOGGER.warning(
                    "Received empty or invalid response from calendar service for %s",
                    calendar_entity,
                )

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error(
                "Error fetching calendar events for %s: %s",
                calendar_entity,
                err,
            )
            # Retain current switch state if calendar lookup times out or fails

        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on manually."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off manually."""
        self._attr_is_on = False
        self.async_write_ha_state()
