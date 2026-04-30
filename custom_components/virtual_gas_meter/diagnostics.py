"""Diagnostics support for Virtual Gas Meter."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.redact import async_redact_data

from .const import CONF_BOILER_ENTITY
from .data import VirtualGasMeterConfigEntry

TO_REDACT = {CONF_BOILER_ENTITY}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: VirtualGasMeterConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator
    state = coordinator.state

    return {
        "entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "minor_version": entry.minor_version,
            "domain": entry.domain,
            "title": entry.title,
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
        },
        "runtime": {
            "last_update_success": coordinator.last_update_success,
            "unit": coordinator.unit,
            "meter_total": round(state.meter_total, 3),
            "consumed_gas": round(state.consumed_gas, 3),
            "heating_interval_minutes": state.heating_interval_minutes,
            "average_rate_per_h": round(state.average_rate_per_h, 3),
            "last_real_meter_timestamp": state.last_real_meter_timestamp.isoformat(),
        },
    }
