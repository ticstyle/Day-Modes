"""Platform for time integration."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_VACATION_MORNING_TIME, DEFAULT_VACATION_MORNING_TIME, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Day modes time platform."""
    config = {**config_entry.data, **config_entry.options}

    device_info = DeviceInfo(
        identifiers={(DOMAIN, config_entry.entry_id)},
        name="Day modes",
        manufacturer="ticstyle",
        model="Day Modes",
    )

    async_add_entities(
        [DayModesVacationTime(config_entry, config, device_info)],
        update_before_add=True,
    )


class DayModesVacationTime(TimeEntity):
    """Representation of the Vacation Morning Time modification entity."""

    _attr_icon = "mdi:clock-digital"
    _attr_has_entity_name = True
    _attr_translation_key = "vacation_morning_time"

    def __init__(
        self, config_entry: ConfigEntry, config: dict[str, Any], device_info: DeviceInfo
    ) -> None:
        """Initialize the time entity."""
        self._config_entry = config_entry
        self._config = config
        self._attr_device_info = device_info
        self._attr_unique_id = f"{config_entry.entry_id}_vacation_morning_time"
        self._attr_name = "Vacation morning time"

    @property
    def native_value(self) -> time:
        """Return the currently configured vacation morning time."""
        time_str = self._config_entry.options.get(
            CONF_VACATION_MORNING_TIME,
            self._config.get(CONF_VACATION_MORNING_TIME, DEFAULT_VACATION_MORNING_TIME),
        )
        return datetime.strptime(time_str, "%H:%M").time()

    async def async_set_value(self, value: time) -> None:
        """Update the option value in the configuration entry live."""
        time_str = value.strftime("%H:%M")
        new_options = {
            **self._config_entry.options,
            CONF_VACATION_MORNING_TIME: time_str,
        }
        self.hass.config_entries.async_update_entry(
            self._config_entry, options=new_options
        )
