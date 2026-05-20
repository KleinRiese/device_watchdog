from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    ATTR_FAILED_ENTITIES,
    ATTR_LAST_UPDATES,
    CONF_ENTITIES,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUTS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
)

@dataclass
class WatchdogState:
    last_updates: dict[str, datetime] = field(default_factory=dict)
    failed_entities: list[str] = field(default_factory=list)
    alarm_active: bool = False


class WatchdogManager:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.entities: list[str] = []
        self.timeouts: dict[str, int] = {}
        self.scan_interval: int = DEFAULT_SCAN_INTERVAL
        self.state = WatchdogState()
        self._unsub_state: Callable[[], None] | None = None
        self._ready = False

        self._load_from_entry(entry)

    def _load_from_entry(self, entry: ConfigEntry) -> None:
        self.entities = list(entry.options.get(CONF_ENTITIES, entry.data.get(CONF_ENTITIES, [])))
        self.timeouts = dict(entry.options.get(CONF_TIMEOUTS, entry.data.get(CONF_TIMEOUTS, {})))
        self.scan_interval = int(entry.options.get(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)))

        for entity_id in self.entities:
            self.timeouts.setdefault(entity_id, DEFAULT_TIMEOUT)

    async def async_start(self) -> None:
        await self._restart_state_listener()
        self._ready = True
        await self.async_check_all()

    async def async_reload(self, entry: ConfigEntry) -> None:
        self.entry = entry
        self._load_from_entry(entry)
        await self.async_start()

    async def async_stop(self) -> None:
        if self._unsub_state:
            self._unsub_state()
            self._unsub_state = None
        self._ready = False

    async def _restart_state_listener(self) -> None:
        if self._unsub_state:
            self._unsub_state()
            self._unsub_state = None

        self._unsub_state = async_track_state_change_event(
            self.hass,
            self.entities,
            self._async_on_state_change,
        )

    @callback
    def _async_on_state_change(self, event: Event) -> None:
        entity_id = event.data.get("entity_id")
        if not entity_id:
            return

        self.state.last_updates[entity_id] = datetime.now(timezone.utc)
        if entity_id in self.state.failed_entities:
            self.state.failed_entities = [e for e in self.state.failed_entities if e != entity_id]

        self.state.alarm_active = bool(self.state.failed_entities)

        self.hass.bus.async_fire(
            f"{DOMAIN}_entity_updated",
            {
                "entity_id": entity_id,
                ATTR_FAILED_ENTITIES: list(self.state.failed_entities),
            },
        )

    def _effective_timeout(self, entity_id: str) -> int:
        return int(self.timeouts.get(entity_id, DEFAULT_TIMEOUT))

    async def async_check_all(self) -> None:
        now = datetime.now(timezone.utc)
        failed: list[str] = []

        for entity_id in self.entities:
            last_update = self.state.last_updates.get(entity_id)
            if last_update is None:
                self.state.last_updates[entity_id] = now
                last_update = now

            timeout = timedelta(seconds=self._effective_timeout(entity_id))
            if now - last_update > timeout:
                failed.append(entity_id)

        self.state.failed_entities = failed
        self.state.alarm_active = bool(failed)

        self.hass.bus.async_fire(
            f"{DOMAIN}_alarm",
            {
                ATTR_FAILED_ENTITIES: list(self.state.failed_entities),
                ATTR_LAST_UPDATES: {
                    entity_id: ts.isoformat()
                    for entity_id, ts in self.state.last_updates.items()
                },
            },
        )

    async def async_time_check(self, _now) -> None:
        if not self._ready:
            return
        await self.async_check_all()

    async def async_force_check(self) -> None:
        await self.async_check_all()