from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_FAILED_ENTITIES, DOMAIN


ENTITY_DESCRIPTION = BinarySensorEntityDescription(
    key="device_watchdog_alarm",
    name="Alarm",
    device_class="problem",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    manager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DeviceWatchdogBinarySensor(manager, entry.entry_id, ENTITY_DESCRIPTION)])


class DeviceWatchdogBinarySensor(BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(self, manager, entry_id: str, description: BinarySensorEntityDescription) -> None:
        self.manager = manager
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{description.key}"

    @property
    def is_on(self) -> bool:
        return self.manager.state.alarm_active

    @property
    def extra_state_attributes(self):
        return {
            ATTR_FAILED_ENTITIES: list(self.manager.state.failed_entities),
        }