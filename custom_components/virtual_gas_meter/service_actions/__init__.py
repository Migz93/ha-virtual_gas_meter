"""Service actions for Virtual Gas Meter."""

from __future__ import annotations

import voluptuous as vol

from custom_components.virtual_gas_meter.const import (
    ATTR_METER_READING,
    ATTR_RECALCULATE_AVERAGE_RATE,
    ATTR_TIMESTAMP,
    DOMAIN,
    LOGGER,
    SERVICE_REAL_METER_READING_UPDATE,
)
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register Virtual Gas Meter services."""

    async def handle_real_meter_reading_update(call: ServiceCall) -> None:
        """Handle the real meter reading update service."""
        entries = hass.config_entries.async_loaded_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("Virtual Gas Meter is not loaded")

        entry = entries[0]
        coordinator = entry.runtime_data.coordinator
        await coordinator.async_handle_real_meter_reading_update(call)

    if hass.services.has_service(DOMAIN, SERVICE_REAL_METER_READING_UPDATE):
        return

    hass.services.async_register(
        DOMAIN,
        SERVICE_REAL_METER_READING_UPDATE,
        handle_real_meter_reading_update,
        schema=vol.Schema(
            {
                vol.Required(ATTR_METER_READING): cv.positive_float,
                vol.Optional(ATTR_TIMESTAMP): cv.datetime,
                vol.Optional(ATTR_RECALCULATE_AVERAGE_RATE, default=True): cv.boolean,
            },
        ),
    )

    LOGGER.debug("Registered Virtual Gas Meter services")


__all__ = ["async_setup_services"]
