"""Consumed gas sensor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.virtual_gas_meter.const import DATA_CONSUMED_GAS, DECIMAL_PLACES, SENSOR_CONSUMED_GAS, UNIT_M3
from custom_components.virtual_gas_meter.entity import VirtualGasMeterEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import UnitOfVolume

if TYPE_CHECKING:
    from custom_components.virtual_gas_meter.coordinator import VirtualGasMeterDataUpdateCoordinator

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key=SENSOR_CONSUMED_GAS,
        name="Virtual Gas Meter Consumed Gas",
        device_class=SensorDeviceClass.GAS,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=DECIMAL_PLACES,
    ),
)


class VirtualGasMeterConsumedGasSensor(SensorEntity, VirtualGasMeterEntity):
    """Sensor exposing estimated gas consumed since the last real reading."""

    def __init__(
        self,
        coordinator: VirtualGasMeterDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def native_value(self) -> float | None:
        """Return the consumed gas since the last real reading."""
        return self.coordinator.data.get(DATA_CONSUMED_GAS)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the configured volume unit."""
        if self.coordinator.unit == UNIT_M3:
            return UnitOfVolume.CUBIC_METERS
        return UnitOfVolume.CENTUM_CUBIC_FEET
