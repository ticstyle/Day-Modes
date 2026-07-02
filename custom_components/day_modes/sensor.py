"""Platform for sensor integration."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_change,
)

from .const import (
    CONF_HOME_ZONE,
    CONF_MORNING_TIME,
    CONF_DAY_TIME,
    CONF_EVENING_TIME,
    CONF_NIGHT_TIME,
    MODE_AWAY,
    MODE_MORNING,
    MODE_DAY,
    MODE_EVENING,
    MODE_NIGHT,
)


def parse_time_string(time_str: str) -> time:
    """Parse time string supporting both HH:MM and legacy HH:MM:SS formats."""
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return datetime.strptime(time_str, "%H:%M:%S").time()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Day modes sensor platform."""
    config = {**config_entry.data, **config_entry.options}

    sensor = DayModesSensor(config_entry.entry_id, config)
    async_add_entities([sensor], update_before_add=True)


class DayModesSensor(SensorEntity):
    """Representation of a Day Mode Sensor."""

    _attr_icon = "mdi:clock-time-four-outline"
    _attr_has_entity_name = False

    def __init__(self, entry_id: str, config: dict[str, Any]) -> None:
        """Initialize the sensor."""
        self._attr_unique_id = f"{entry_id}_sensor"
        self._attr_name = "Day modes"
        self.entity_id = "sensor.day_modes"
        self._config = config
        self._unsub_listeners: list[Any] = []

        # Parse string times safely to time objects
        self._times = {
            MODE_MORNING: parse_time_string(config[CONF_MORNING_TIME]),
            MODE_DAY: parse_time_string(config[CONF_DAY_TIME]),
            MODE_EVENING: parse_time_string(config[CONF_EVENING_TIME]),
            MODE_NIGHT: parse_time_string(config[CONF_NIGHT_TIME]),
        }

    async def async_added_to_hass(self) -> None:
        """Register listeners when added to hass."""

        @callback
        def async_state_changed_listener(event: Event) -> None:
            """Handle zone state changes."""
            self._update_state()

        self._unsub_listeners.append(
            async_track_state_change_event(
                self.hass,
                [self._config[CONF_HOME_ZONE]],
                async_state_changed_listener,
            )
        )

        for mode_time in self._times.values():
            self._unsub_listeners.append(
                async_track_time_change(
                    self.hass,
                    self._async_time_listener,
                    hour=mode_time.hour,
                    minute=mode_time.minute,
                    second=mode_time.second,
                )
            )

        self._update_state()

    async def async_will_remove_from_hass(self) -> None:
        """Clean up listeners when removing entity."""
        for unsub in self._unsub_listeners:
            unsub()
        self._unsub_listeners.clear()

    @callback
    def _async_time_listener(self, now: datetime) -> None:
        """Handle time-based state updates."""
        self._update_state()

    def _update_state(self) -> None:
        """Calculate and set the current state of the sensor."""
        zone_entity = self._config[CONF_HOME_ZONE]
        zone_state = self.hass.states.get(zone_entity)

        if zone_state is None or zone_state.state == STATE_UNKNOWN:
            zone_count = 0
        else:
            try:
                zone_count = int(float(zone_state.state))
            except ValueError:
                zone_count = 0

        if zone_count < 1:
            self._attr_native_value = MODE_AWAY
            self.async_write_ha_state()
            return

        current_time = datetime.now().time()
        t_morning = self._times[MODE_MORNING]
        t_day = self._times[MODE_DAY]
        t_evening = self._times[MODE_EVENING]
        t_night = self._times[MODE_NIGHT]

        if t_morning <= current_time < t_day:
            calculated_mode = MODE_MORNING
        elif t_day <= current_time < t_evening:
            calculated_mode = MODE_DAY
        elif t_evening <= current_time < t_night:
            calculated_mode = MODE_EVENING
        else:
            calculated_mode = MODE_NIGHT

        self._attr_native_value = calculated_mode
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes reflecting current setups."""
        return {
            "tracked_zone": self._config[CONF_HOME_ZONE],
            "morning_time": self._config[CONF_MORNING_TIME],
            "day_time": self._config[CONF_DAY_TIME],
            "evening_time": self._config[CONF_EVENING_TIME],
            "night_time": self._config[CONF_NIGHT_TIME],
        }
