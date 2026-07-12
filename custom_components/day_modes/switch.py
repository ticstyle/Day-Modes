"""Platform for switch integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_VACATION_CALENDAR, DOMAIN


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
    """Representation of the Vacation Mode Switch."""

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
        """Track the calendar state if configured."""
        calendar_entity = self._config.get(CONF_VACATION_CALENDAR)
        if not calendar_entity:
            return

        @callback
        def async_calendar_listener(event: Event[EventStateChangedData]) -> None:
            """Handle calendar state changes."""
            self._update_from_calendar()

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [calendar_entity],
                async_calendar_listener,
            )
        )
        self._update_from_calendar()

    def _update_from_calendar(self) -> None:
        """Check the calendar state and turn the switch on or off."""
        calendar_entity = self._config.get(CONF_VACATION_CALENDAR)
        if not calendar_entity:
            return

        state = self.hass.states.get(calendar_entity)
        if state and state.state == "on":
            self._attr_is_on = True
        else:
            self._attr_is_on = False
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self._attr_is_on = False
        self.async_write_ha_state()
