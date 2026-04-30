"""Base entity for Virtual Gas Meter."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.virtual_gas_meter.const import ATTRIBUTION
from custom_components.virtual_gas_meter.entity_utils.device_info import get_device_info
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from custom_components.virtual_gas_meter.coordinator import VirtualGasMeterDataUpdateCoordinator
    from homeassistant.helpers.entity import EntityDescription


class VirtualGasMeterEntity(CoordinatorEntity["VirtualGasMeterDataUpdateCoordinator"]):
    """Base entity for Virtual Gas Meter entities."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = False

    def __init__(
        self,
        coordinator: VirtualGasMeterDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = get_device_info(coordinator.config_entry)
