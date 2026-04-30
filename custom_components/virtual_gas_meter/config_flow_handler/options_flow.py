"""Options flow for Virtual Gas Meter."""

from __future__ import annotations

from typing import Any

from custom_components.virtual_gas_meter.config_flow_handler.schemas import get_options_schema
from custom_components.virtual_gas_meter.config_flow_handler.validators import validate_boiler_entity
from custom_components.virtual_gas_meter.const import CONF_AVERAGE_RATE, CONF_BOILER_ENTITY, CONF_UNIT, LOGGER
from homeassistant import config_entries


class VirtualGasMeterOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Virtual Gas Meter."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Manage options."""
        errors: dict[str, str] = {}

        coordinator = self.config_entry.runtime_data.coordinator

        if user_input is not None:
            errors.update(validate_boiler_entity(self.hass, user_input[CONF_BOILER_ENTITY]))

            if user_input[CONF_AVERAGE_RATE] <= 0:
                errors[CONF_AVERAGE_RATE] = "must_be_positive"

            if not errors:
                new_data = {**self.config_entry.data, CONF_BOILER_ENTITY: user_input[CONF_BOILER_ENTITY]}
                self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)

                coordinator.state.average_rate_per_h = user_input[CONF_AVERAGE_RATE]
                await coordinator.async_save_data()

                LOGGER.info("Updated average gas consumption rate to %.3f", user_input[CONF_AVERAGE_RATE])
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)

                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=get_options_schema(
                boiler_entity=self.config_entry.data[CONF_BOILER_ENTITY],
                average_rate=coordinator.state.average_rate_per_h,
            ),
            errors=errors,
            description_placeholders={
                "current_unit": self.config_entry.data[CONF_UNIT],
                "info": (
                    "You can change the boiler entity and average hourly consumption rate. "
                    "Unit and initial meter reading cannot be modified."
                ),
            },
        )


__all__ = ["VirtualGasMeterOptionsFlow"]
