"""Runtime data types for Virtual Gas Meter."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import VirtualGasMeterDataUpdateCoordinator

type VirtualGasMeterConfigEntry = ConfigEntry[VirtualGasMeterData]


@dataclass(slots=True)
class VirtualGasMeterData:
    """Runtime data attached to a config entry."""

    coordinator: VirtualGasMeterDataUpdateCoordinator
    integration: Integration


@dataclass(slots=True)
class VirtualGasMeterState:
    """Current calculated gas meter state."""

    last_real_meter_reading: float
    last_real_meter_timestamp: datetime
    average_rate_per_h: float
    consumed_gas: float
    heating_interval_minutes: int

    @property
    def meter_total(self) -> float:
        """Return the virtual meter total."""
        return self.last_real_meter_reading + self.consumed_gas
