"""Diagnostics support for Day modes."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import CONF_HOME_ZONE, CONF_VACATION_CALENDAR

# Sensitive keys that must be masked inside the diagnostics dump
TO_REDACT = {
    CONF_HOME_ZONE,
    CONF_VACATION_CALENDAR,
    "tracked_zone",
    "vacation_calendar",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry, safe for public GitHub sharing."""
    # Redact config entry baseline data and options
    redacted_data = async_redact_data(dict(config_entry.data), TO_REDACT)
    redacted_options = async_redact_data(dict(config_entry.options), TO_REDACT)

    # Resolve and grab all entities registered under this config entry
    entity_reg = er.async_get(hass)
    entities = er.async_entries_for_config_entry(entity_reg, config_entry.entry_id)

    redacted_entities = {}
    for entity in entities:
        state = hass.states.get(entity.entity_id)
        if state is not None:
            # Safely log the state and redact all attributes containing sensitive setups
            redacted_entities[entity.entity_id] = {
                "state": state.state,
                "attributes": async_redact_data(dict(state.attributes), TO_REDACT),
            }

    return {
        "config_entry": {
            "entry_id": config_entry.entry_id,
            "version": config_entry.version,
            "data": redacted_data,
            "options": redacted_options,
        },
        "entities": redacted_entities,
    }
