"""Device info helpers for Virtual Gas Meter."""

from __future__ import annotations

from custom_components.virtual_gas_meter.const import DEVICE_MANUFACTURER, DEVICE_MODEL, DEVICE_NAME
from custom_components.virtual_gas_meter.data import VirtualGasMeterConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo


def get_device_info(config_entry: VirtualGasMeterConfigEntry) -> DeviceInfo:
    """Return device info shared by all Virtual Gas Meter entities."""
    return DeviceInfo(
        identifiers={(config_entry.domain, config_entry.entry_id)},
        name=DEVICE_NAME,
        manufacturer=DEVICE_MANUFACTURER,
        model=DEVICE_MODEL,
    )


__all__ = ["get_device_info"]
