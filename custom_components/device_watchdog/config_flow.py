from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONF_ENTITIES,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUTS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
)

def _schema_basic(default_entities=None, default_scan_interval=DEFAULT_SCAN_INTERVAL):
    return vol.Schema(
        {
            vol.Required(
                CONF_ENTITIES,
                default=default_entities or [],
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(multiple=True)
            ),
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=default_scan_interval,
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=5,
                    max=3600,
                    step=5,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
        }
    )


class DeviceWatchdogConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=_schema_basic(),
            )

        entities = user_input[CONF_ENTITIES]
        scan_interval = int(user_input[CONF_SCAN_INTERVAL])

        timeouts = {entity_id: DEFAULT_TIMEOUT for entity_id in entities}

        return self.async_create_entry(
            title="Device Watchdog",
            data={
                CONF_ENTITIES: entities,
                CONF_TIMEOUTS: timeouts,
                CONF_SCAN_INTERVAL: scan_interval,
            },
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return DeviceWatchdogOptionsFlow(config_entry)


class DeviceWatchdogOptionsFlow(config_entries.OptionsFlowWithReload):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        entities = list(self.config_entry.options.get(CONF_ENTITIES, self.config_entry.data.get(CONF_ENTITIES, [])))
        timeouts = dict(self.config_entry.options.get(CONF_TIMEOUTS, self.config_entry.data.get(CONF_TIMEOUTS, {})))
        scan_interval = int(self.config_entry.options.get(CONF_SCAN_INTERVAL, self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)))

        if user_input is not None:
            new_entities = user_input[CONF_ENTITIES]
            new_scan_interval = int(user_input[CONF_SCAN_INTERVAL])

            new_timeouts = {}
            for entity_id in new_entities:
                key = f"timeout__{entity_id}"
                new_timeouts[entity_id] = int(user_input.get(key, DEFAULT_TIMEOUT))

            return self.async_create_entry(
                data={
                    CONF_ENTITIES: new_entities,
                    CONF_TIMEOUTS: new_timeouts,
                    CONF_SCAN_INTERVAL: new_scan_interval,
                }
            )

        fields = {
            vol.Required(CONF_ENTITIES, default=entities): selector.EntitySelector(
                selector.EntitySelectorConfig(multiple=True)
            ),
            vol.Required(CONF_SCAN_INTERVAL, default=scan_interval): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=5,
                    max=3600,
                    step=5,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
        }

        for entity_id in entities:
            fields[vol.Required(f"timeout__{entity_id}", default=int(timeouts.get(entity_id, DEFAULT_TIMEOUT)))] = selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=5,
                    max=86400,
                    step=5,
                    mode=selector.NumberSelectorMode.BOX,
                )
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(fields),
        )