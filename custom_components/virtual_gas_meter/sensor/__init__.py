"""Sensor platform for Virtual Gas Meter."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.virtual_gas_meter.const import (
    DEFAULT_ENTITY_ID_CONSUMED_GAS,
    DEFAULT_ENTITY_ID_HEATING_INTERVAL,
    DEFAULT_ENTITY_ID_TOTAL,
    PARALLEL_UPDATES,
)
from custom_components.virtual_gas_meter.sensor.consumed_gas import (
    ENTITY_DESCRIPTIONS as CONSUMED_GAS_DESCRIPTIONS,
    VirtualGasMeterConsumedGasSensor,
)
from custom_components.virtual_gas_meter.sensor.heating_interval import (
    ENTITY_DESCRIPTIONS as HEATING_INTERVAL_DESCRIPTIONS,
    VirtualGasMeterHeatingIntervalSensor,
)
from custom_components.virtual_gas_meter.sensor.meter_total import (
    ENTITY_DESCRIPTIONS as METER_TOTAL_DESCRIPTIONS,
    VirtualGasMeterTotalSensor,
)
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.helpers import entity_registry as er

if TYPE_CHECKING:
    from custom_components.virtual_gas_meter.data import VirtualGasMeterConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

ENTITY_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    *METER_TOTAL_DESCRIPTIONS,
    *CONSUMED_GAS_DESCRIPTIONS,
    *HEATING_INTERVAL_DESCRIPTIONS,
)

DEFAULT_ENTITY_IDS = {
    METER_TOTAL_DESCRIPTIONS[0].key: DEFAULT_ENTITY_ID_TOTAL,
    CONSUMED_GAS_DESCRIPTIONS[0].key: DEFAULT_ENTITY_ID_CONSUMED_GAS,
    HEATING_INTERVAL_DESCRIPTIONS[0].key: DEFAULT_ENTITY_ID_HEATING_INTERVAL,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VirtualGasMeterConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Virtual Gas Meter sensors."""
    coordinator = entry.runtime_data.coordinator

    _ensure_default_entity_ids(hass, entry)

    async_add_entities(
        [
            VirtualGasMeterTotalSensor(coordinator, METER_TOTAL_DESCRIPTIONS[0]),
            VirtualGasMeterConsumedGasSensor(coordinator, CONSUMED_GAS_DESCRIPTIONS[0]),
            VirtualGasMeterHeatingIntervalSensor(coordinator, HEATING_INTERVAL_DESCRIPTIONS[0]),
        ],
    )


def _ensure_default_entity_ids(hass: HomeAssistant, entry: VirtualGasMeterConfigEntry) -> None:
    """Pre-create entity registry entries so new installs get the intended entity IDs."""
    entity_registry = er.async_get(hass)

    for description in ENTITY_DESCRIPTIONS:
        unique_id = f"{entry.entry_id}_{description.key}"
        if entity_registry.async_get_entity_id("sensor", entry.domain, unique_id) is not None:
            continue

        entity_registry.async_get_or_create(
            "sensor",
            entry.domain,
            unique_id,
            suggested_object_id=DEFAULT_ENTITY_IDS[description.key].removeprefix("sensor."),
            config_entry=entry,
            original_name=description.name,
        )


__all__ = ["PARALLEL_UPDATES", "async_setup_entry"]
