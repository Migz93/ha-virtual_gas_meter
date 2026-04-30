"""Config flow for Virtual Gas Meter."""

from __future__ import annotations

from typing import Any

from custom_components.virtual_gas_meter.config_flow_handler.options_flow import VirtualGasMeterOptionsFlow
from custom_components.virtual_gas_meter.config_flow_handler.schemas import get_options_schema, get_user_schema
from custom_components.virtual_gas_meter.config_flow_handler.validators import validate_boiler_entity
from custom_components.virtual_gas_meter.const import (
    CONF_AVERAGE_RATE,
    CONF_BOILER_ENTITY,
    CONF_INITIAL_AVERAGE_RATE,
    CONF_INITIAL_METER_READING,
    CONF_UNIT,
    DOMAIN,
)
from homeassistant import config_entries


class VirtualGasMeterConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Virtual Gas Meter."""

    VERSION = 1
    MINOR_VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> VirtualGasMeterOptionsFlow:
        """Return the options flow."""
        return VirtualGasMeterOptionsFlow()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial setup step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}

        if user_input is not None:
            errors.update(validate_boiler_entity(self.hass, user_input[CONF_BOILER_ENTITY]))

            if user_input[CONF_INITIAL_AVERAGE_RATE] <= 0:
                errors[CONF_INITIAL_AVERAGE_RATE] = "must_be_positive"

            if not errors:
                data = {
                    CONF_BOILER_ENTITY: user_input[CONF_BOILER_ENTITY],
                    CONF_UNIT: user_input[CONF_UNIT],
                    CONF_INITIAL_METER_READING: user_input[CONF_INITIAL_METER_READING],
                    CONF_INITIAL_AVERAGE_RATE: user_input[CONF_INITIAL_AVERAGE_RATE],
                }
                return self.async_create_entry(
                    title="Virtual Gas Meter",
                    data=data,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=get_user_schema(user_input),
            errors=errors,
            description_placeholders={
                "unit_note": "Unit selection cannot be changed after setup.",
            },
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle reconfiguration for existing config entries."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            errors.update(validate_boiler_entity(self.hass, user_input[CONF_BOILER_ENTITY]))

            if user_input[CONF_AVERAGE_RATE] <= 0:
                errors[CONF_AVERAGE_RATE] = "must_be_positive"

            if not errors:
                new_data = {**entry.data, CONF_BOILER_ENTITY: user_input[CONF_BOILER_ENTITY]}
                coordinator = entry.runtime_data.coordinator
                coordinator.state.average_rate_per_h = user_input[CONF_AVERAGE_RATE]
                await coordinator.async_save_data()

                return self.async_update_reload_and_abort(
                    entry,
                    data=new_data,
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=get_options_schema(
                boiler_entity=entry.data[CONF_BOILER_ENTITY],
                average_rate=entry.runtime_data.coordinator.state.average_rate_per_h,
            ),
            errors=errors,
        )
