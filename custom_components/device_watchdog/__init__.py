from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .watchdog import WatchdogManager

type DeviceWatchdogConfigEntry = ConfigEntry


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: DeviceWatchdogConfigEntry) -> bool:
    manager = WatchdogManager(hass, entry)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = manager

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await manager.async_start()

    async def _update_listener(hass_: HomeAssistant, entry_: ConfigEntry) -> None:
        manager_ = hass_.data[DOMAIN][entry_.entry_id]
        await manager_.async_reload(entry_)

    entry.async_on_unload(entry.add_update_listener(_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DeviceWatchdogConfigEntry) -> bool:
    manager = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if manager:
        await manager.async_stop()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok and DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok