"""Options flow schemas for Virtual Gas Meter."""

from __future__ import annotations

import voluptuous as vol

from custom_components.virtual_gas_meter.const import ALLOWED_BOILER_DOMAINS, CONF_AVERAGE_RATE, CONF_BOILER_ENTITY
from homeassistant.helpers import config_validation as cv, selector


def get_options_schema(boiler_entity: str, average_rate: float) -> vol.Schema:
    """Return the options schema."""
    return vol.Schema(
        {
            vol.Required(CONF_BOILER_ENTITY, default=boiler_entity): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=ALLOWED_BOILER_DOMAINS),
            ),
            vol.Required(CONF_AVERAGE_RATE, default=average_rate): cv.positive_float,
        },
    )


__all__ = ["get_options_schema"]
