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


def _entity_selector():
    return selector.EntitySelector(
        selector.EntitySelectorConfig(multiple=True)
    )


def _number_selector(min_value, max_value, step=5):
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=min_value,
            max=max_value,
            step=step,
            mode=selector.NumberSelectorMode.BOX,
        )
    )


class DeviceWatchdogConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_ENTITIES, default=[]): _entity_selector(),
                        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): _number_selector(5, 3600),
                    }
                ),
            )

        entities = list(user_input[CONF_ENTITIES])
        scan_interval = int(user_input[CONF_SCAN_INTERVAL])

        return self.async_create_entry(
            title="Device Watchdog",
            data={
                CONF_ENTITIES: entities,
                CONF_TIMEOUTS: {entity_id: DEFAULT_TIMEOUT for entity_id in entities},
                CONF_SCAN_INTERVAL: scan_interval,
            },
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return DeviceWatchdogOptionsFlow()


class DeviceWatchdogOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        current_entities = list(
            self.config_entry.options.get(
                CONF_ENTITIES,
                self.config_entry.data.get(CONF_ENTITIES, []),
            )
        )
        current_scan_interval = int(
            self.config_entry.options.get(
                CONF_SCAN_INTERVAL,
                self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            )
        )

        if user_input is not None:
            new_entities = list(user_input[CONF_ENTITIES])
            new_scan_interval = int(user_input[CONF_SCAN_INTERVAL])

            return self.async_create_entry(
                data={
                    CONF_ENTITIES: new_entities,
                    CONF_SCAN_INTERVAL: new_scan_interval,
                }
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ENTITIES, default=current_entities): _entity_selector(),
                    vol.Required(CONF_SCAN_INTERVAL, default=current_scan_interval): _number_selector(5, 3600),
                }
            ),
        )

    async def async_step_timeouts(self, user_input=None):
        entities = list(self.config_entry.options.get(CONF_ENTITIES, self.config_entry.data.get(CONF_ENTITIES, [])))
        current_timeouts = dict(
            self.config_entry.options.get(
                CONF_TIMEOUTS,
                self.config_entry.data.get(CONF_TIMEOUTS, {}),
            )
        )

        if user_input is not None:
            new_timeouts = {
                entity_id: int(user_input[f"timeout__{entity_id}"])
                for entity_id in entities
            }

            return self.async_create_entry(
                data={
                    CONF_TIMEOUTS: new_timeouts,
                }
            )

        schema = {}
        for entity_id in entities:
            schema[
                vol.Required(
                    f"timeout__{entity_id}",
                    default=int(current_timeouts.get(entity_id, DEFAULT_TIMEOUT)),
                )
            ] = _number_selector(5, 86400)

        return self.async_show_form(
            step_id="timeouts",
            data_schema=vol.Schema(schema),
        )