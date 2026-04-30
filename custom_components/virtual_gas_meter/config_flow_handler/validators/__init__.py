"""Validation helpers for Virtual Gas Meter config flows."""

from __future__ import annotations

from custom_components.virtual_gas_meter.const import ALLOWED_BOILER_DOMAINS
from homeassistant.core import HomeAssistant


def validate_boiler_entity(hass: HomeAssistant, entity_id: str) -> dict[str, str]:
    """Validate a configured boiler entity."""
    errors: dict[str, str] = {}
    domain = entity_id.split(".", maxsplit=1)[0] if "." in entity_id else ""

    if domain not in ALLOWED_BOILER_DOMAINS:
        errors["boiler_entity_id"] = "invalid_domain"
    elif hass.states.get(entity_id) is None:
        errors["boiler_entity_id"] = "entity_not_found"

    return errors


__all__ = ["validate_boiler_entity"]
