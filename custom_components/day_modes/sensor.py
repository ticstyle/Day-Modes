"""Platform for sensor integration."""

from __future annotations

from datetime import datetime, time
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_change,
)

from .const import (
    CONF_DAY_TIME,
    CONF_EVENING_TIME,
    CONF_HOME_ZONE,
    CONF_MORNING_TIME,
    CONF_NIGHT_TIME,
    CONF_SCHEDULES,
    CONF_VACATION_CALENDAR,
    CONF_VACATION_MORNING_TIME,
    DEFAULT_VACATION_MORNING_TIME,
    DOMAIN,
    MODE_AWAY,
    MODE_DAY,
    MODE_EVENING,
    MODE_MORNING,
    MODE_NIGHT,
    WEEKDAYS,
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
    """Set up the Day modes sensor platform and time entities."""
    config = {**config_entry.data, **config_entry.options}

    device_info = DeviceInfo(
        identifiers={(DOMAIN, config_entry.entry_id)},
        name="Day modes",
        manufacturer="ticstyle",
        model="Day Modes",
    )

    entities = [
        DayModesSensor(config_entry.entry_id, config, device_info),
        DayModesVacationCalendarSensor(config_entry.entry_id, config, device_info),
        DayModesTimeSensor(
            config_entry.entry_id, config, CONF_MORNING_TIME, device_info
        ),
        DayModesTimeSensor(config_entry.entry_id, config, CONF_DAY_TIME, device_info),
        DayModesTimeSensor(
            config_entry.entry_id, config, CONF_EVENING_TIME, device_info
        ),
        DayModesTimeSensor(
            config_entry.entry_id, config, CONF_NIGHT_TIME, device_info
        ),
    ]

    async_add_entities(entities, update_before_add=True)


class DayModesSensor(SensorEntity):
    """Representation of the core Day Mode State Sensor tracking multi-day matrixes."""

    _attr_icon = "mdi:home-clock"
    _attr_has_entity_name = True
    _attr_translation_key = "current_mode"

    def __init__(
        self, entry_id: str, config: dict[str, Any], device_info: DeviceInfo
    ) -> None:
        """Initialize the sensor."""
        self._attr_unique_id = f"{entry_id}_sensor"
        self._config = config
        self._attr_device_info = device_info
        self._attr_name = "Current mode"
        self._unsub_listeners: list[Any] = []

    async def async_added_to_hass(self) -> None:
        """Register dynamic listeners for time boundaries and midnight roll-overs."""

        @callback
        def async_state_changed_listener(event: Event[EventStateChangedData]) -> None:
            """Handle zone state changes."""
            self._update_state()

        @callback
        def async_switch_listener(event: Event[EventStateChangedData]) -> None:
            """Handle vacation switch shifts directly."""
            self._update_state()

        self._unsub_listeners.append(
            async_track_state_change_event(
                self.hass,
                [self._config[CONF_HOME_ZONE]],
                async_state_changed_listener,
            )
        )

        self._unsub_listeners.append(
            async_track_state_change_event(
                self.hass,
                ["switch.day_modes_vacation_mode"],
                async_switch_listener,
            )
        )

        for schedule in self._config.get(CONF_SCHEDULES, []):
            for key in [
                CONF_MORNING_TIME,
                CONF_DAY_TIME,
                CONF_EVENING_TIME,
                CONF_NIGHT_TIME,
            ]:
                boundary_time = parse_time_string(schedule[key])
                self._unsub_listeners.append(
                    async_track_time_change(
                        self.hass,
                        self._async_event_listener,
                        hour=boundary_time.hour,
                        minute=boundary_time.minute,
                        second=boundary_time.second,
                    )
                )

        self._unsub_listeners.append(
            async_track_time_change(
                self.hass, self._async_event_listener, hour=0, minute=0, second=0
            )
        )

        self._update_state()

    async def async_will_remove_from_hass(self) -> None:
        """Clean up listeners when removing entity."""
        for unsub in self._unsub_listeners:
            unsub()
        self._unsub_listeners.clear()

    @callback
    def _async_event_listener(self, now: datetime) -> None:
        """Trigger evaluation when time ticks over schedules or midnights."""
        self._update_state()

    def _get_active_times(self) -> dict[str, time] | None:
        """Extract the exact active schedule profile mapped to the current day string."""
        current_weekday_num = datetime.now().weekday()
        current_weekday_str = WEEKDAYS.get(current_weekday_num)

        for schedule in self._config.get(CONF_SCHEDULES, []):
            if current_weekday_str in schedule["days"]:
                return {
                    MODE_MORNING: parse_time_string(schedule[CONF_MORNING_TIME]),
                    MODE_DAY: parse_time_string(schedule[CONF_DAY_TIME]),
                    MODE_EVENING: parse_time_string(schedule[CONF_EVENING_TIME]),
                    MODE_NIGHT: parse_time_string(schedule[CONF_NIGHT_TIME]),
                }
        return None

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

        times = self._get_active_times()
        if not times:
            self._attr_native_value = STATE_UNKNOWN
            self.async_write_ha_state()
            return

        vacation_state = self.hass.states.get("switch.day_modes_vacation_mode")
        is_vacation = vacation_state is not None and vacation_state.state == "on"

        current_time = datetime.now().time()

        if is_vacation:
            vacation_time_str = self._config.get(
                CONF_VACATION_MORNING_TIME, DEFAULT_VACATION_MORNING_TIME
            )
            t_morning = parse_time_string(vacation_time_str)
        else:
            t_morning = times[MODE_MORNING]

        t_day = times[MODE_DAY]
        t_evening = times[MODE_EVENING]
        t_night = times[MODE_NIGHT]

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
        """Return full matrix layout tracking data packaged for UI rendering."""
        schedules_data = []
        for idx, schedule in enumerate(self._config.get(CONF_SCHEDULES, [])):
            days_list = [d.capitalize() for d in schedule.get("days", [])]
            schedules_data.append(
                {
                    "profile": idx + 1,
                    "days": days_list,
                    "morning": schedule.get(CONF_MORNING_TIME),
                    "day": schedule.get(CONF_DAY_TIME),
                    "evening": schedule.get(CONF_EVENING_TIME),
                    "night": schedule.get(CONF_NIGHT_TIME),
                }
            )

        return {
            "tracked_zone": self._config[CONF_HOME_ZONE],
            "schedules": schedules_data,
        }


class DayModesVacationCalendarSensor(SensorEntity):
    """Representation of the vacation calendar configuration sensor."""

    _attr_icon = "mdi:calendar-status"
    _attr_has_entity_name = True
    _attr_translation_key = "vacation_calendar"

    def __init__(
        self, entry_id: str, config: dict[str, Any], device_info: DeviceInfo
    ) -> None:
        """Initialize the sensor."""
        self._attr_unique_id = f"{entry_id}_vacation_calendar"
        self._config = config
        self._attr_device_info = device_info
        self._attr_name = "Vacation calendar"

    @property
    def native_value(self) -> str:
        """Return the monitored calendar entity or Not Configured."""
        return self._config.get(CONF_VACATION_CALENDAR) or "Not Configured"


class DayModesTimeSensor(SensorEntity):
    """Representation of a dynamic calendar-aware time configuration entity."""

    _attr_icon = "mdi:clock-outline"
    _attr_has_entity_name = True

    def __init__(
        self,
        entry_id: str,
        config: dict[str, Any],
        config_key: str,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the time sensor."""
        self._attr_unique_id = f"{entry_id}_{config_key}"
        self._attr_translation_key = config_key
        self._attr_device_info = device_info
        self._config = config
        self._config_key = config_key

        names = {
            CONF_MORNING_TIME: "Morning start time",
            CONF_DAY_TIME: "Day start time",
            CONF_EVENING_TIME: "Evening start time",
            CONF_NIGHT_TIME: "Night start time",
        }
        self._attr_name = names.get(config_key)

    @property
    def native_value(self) -> str | None:
        """Return the dynamically isolated schedule time assigned to today."""
        if self._config_key == CONF_MORNING_TIME:
            vacation_state = self.hass.states.get("switch.day_modes_vacation_mode")
            if vacation_state and vacation_state.state == "on":
                return self._config.get(
                    CONF_VACATION_MORNING_TIME, DEFAULT_VACATION_MORNING_TIME
                )

        current_weekday_num = datetime.now().weekday()
        current_weekday_str = WEEKDAYS.get(current_weekday_num)

        for schedule in self._config.get(CONF_SCHEDULES, []):
            if current_weekday_str in schedule["days"]:
                return schedule.get(self._config_key)
        return None
