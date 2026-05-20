from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_FAILED_ENTITIES, ATTR_LAST_UPDATES, DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    manager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DeviceWatchdogSummarySensor(manager, entry.entry_id)])


class DeviceWatchdogSummarySensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, manager, entry_id: str) -> None:
        self.manager = manager
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_summary"
        self._attr_name = "Summary"

    @property
    def native_value(self):
        return "alarm" if self.manager.state.alarm_active else "ok"

    @property
    def extra_state_attributes(self):
        return {
            ATTR_FAILED_ENTITIES: list(self.manager.state.failed_entities),
            ATTR_LAST_UPDATES: {
                entity_id: ts.isoformat()
                for entity_id, ts in self.manager.state.last_updates.items()
            },
        }