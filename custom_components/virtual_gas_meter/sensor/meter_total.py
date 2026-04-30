"""Virtual gas meter total sensor."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_components.virtual_gas_meter.const import (
    DATA_METER_TOTAL,
    DECIMAL_PLACES,
    SENSOR_VIRTUAL_GAS_METER_TOTAL,
    UNIT_M3,
)
from custom_components.virtual_gas_meter.entity import VirtualGasMeterEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import UnitOfVolume

if TYPE_CHECKING:
    from custom_components.virtual_gas_meter.coordinator import VirtualGasMeterDataUpdateCoordinator

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key=SENSOR_VIRTUAL_GAS_METER_TOTAL,
        translation_key="meter_total",
        name="Virtual Gas Meter Total",
        device_class=SensorDeviceClass.GAS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=DECIMAL_PLACES,
    ),
)


class VirtualGasMeterTotalSensor(SensorEntity, VirtualGasMeterEntity):
    """Sensor exposing the estimated absolute gas meter total."""

    def __init__(
        self,
        coordinator: VirtualGasMeterDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def native_value(self) -> float | None:
        """Return the current virtual meter total."""
        return self.coordinator.data.get(DATA_METER_TOTAL)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the configured volume unit."""
        if self.coordinator.unit == UNIT_M3:
            return UnitOfVolume.CUBIC_METERS
        return UnitOfVolume.CENTUM_CUBIC_FEET

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return calibration attributes."""
        state = self.coordinator.state
        return {
            "last_real_meter_reading": round(state.last_real_meter_reading, DECIMAL_PLACES),
            "last_real_meter_timestamp": state.last_real_meter_timestamp.isoformat(),
            "average_rate_per_h": f"{state.average_rate_per_h:.{DECIMAL_PLACES}f}",
            "boiler_entity_id": self.coordinator.boiler_entity_id,
            "unit": self.coordinator.unit,
        }
