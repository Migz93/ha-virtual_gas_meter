"""Heating interval sensor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.virtual_gas_meter.const import DATA_HEATING_INTERVAL, SENSOR_HEATING_INTERVAL
from custom_components.virtual_gas_meter.entity import VirtualGasMeterEntity
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

if TYPE_CHECKING:
    from custom_components.virtual_gas_meter.coordinator import VirtualGasMeterDataUpdateCoordinator

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key=SENSOR_HEATING_INTERVAL,
        name="Virtual Gas Meter Heating Interval",
        icon="mdi:clock-outline",
    ),
)


class VirtualGasMeterHeatingIntervalSensor(SensorEntity, VirtualGasMeterEntity):
    """Sensor exposing boiler runtime since the last real reading."""

    def __init__(
        self,
        coordinator: VirtualGasMeterDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def native_value(self) -> str | None:
        """Return the heating interval display string."""
        return self.coordinator.data.get(DATA_HEATING_INTERVAL)
