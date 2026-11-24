"""Config flow schemas for Virtual Gas Meter."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import probatio

from custom_components.virtual_gas_meter.const import (
    ALLOWED_BOILER_DOMAINS,
    CONF_BOILER_ENTITY,
    CONF_INITIAL_AVERAGE_RATE,
    CONF_INITIAL_METER_READING,
    CONF_UNIT,
    UNIT_CCF,
    UNIT_M3,
)
from homeassistant.helpers import config_validation as cv, selector


def get_user_schema(defaults: Mapping[str, Any] | None = None) -> probatio.Schema:
    """Return the user setup schema."""
    defaults = defaults or {}

    return probatio.Schema(
        {
            probatio.Required(CONF_BOILER_ENTITY, default=defaults.get(CONF_BOILER_ENTITY, probatio.UNDEFINED)): (
                selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=ALLOWED_BOILER_DOMAINS),
                )
            ),
            probatio.Required(CONF_UNIT, default=defaults.get(CONF_UNIT, UNIT_M3)): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value=UNIT_M3, label="Cubic Meters (m3)"),
                        selector.SelectOptionDict(value=UNIT_CCF, label="Hundred Cubic Feet (CCF)"),
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                ),
            ),
            probatio.Required(
                CONF_INITIAL_METER_READING,
                default=defaults.get(CONF_INITIAL_METER_READING, 0.0),
            ): cv.positive_float,
            probatio.Required(
                CONF_INITIAL_AVERAGE_RATE,
                default=defaults.get(CONF_INITIAL_AVERAGE_RATE, 0.0),
            ): cv.positive_float,
        },
    )


__all__ = ["get_user_schema"]
