"""The Day modes integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_VACATION_MORNING_TIME, DEFAULT_VACATION_MORNING_TIME, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.TIME]


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry from previous versions."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        hass.config_entries.async_update_entry(config_entry, version=2)

    if config_entry.version == 2:
        new_options = {**config_entry.options}
        if CONF_VACATION_MORNING_TIME not in new_options:
            new_options[CONF_VACATION_MORNING_TIME] = DEFAULT_VACATION_MORNING_TIME

        hass.config_entries.async_update_entry(
            config_entry,
            version=3,
            options=new_options,
        )

    _LOGGER.info("Migration to version %s successful", config_entry.version)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Day modes from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Forward the setup to all integrated platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for option updates to reload the entity dynamically
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)
