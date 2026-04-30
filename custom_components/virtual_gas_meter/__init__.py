"""Virtual Gas Meter integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.loader import async_get_loaded_integration

from .const import DOMAIN, LOGGER
from .coordinator import VirtualGasMeterDataUpdateCoordinator
from .data import VirtualGasMeterConfigEntry, VirtualGasMeterData
from .service_actions import async_setup_services

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration and register service actions."""
    await async_setup_services(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VirtualGasMeterConfigEntry,
) -> bool:
    """Set up Virtual Gas Meter from a config entry."""
    coordinator = VirtualGasMeterDataUpdateCoordinator(hass, LOGGER, entry)

    entry.runtime_data = VirtualGasMeterData(
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    LOGGER.info("Virtual Gas Meter loaded")

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: VirtualGasMeterConfigEntry,
) -> bool:
    """Unload a config entry."""
    await entry.runtime_data.coordinator.async_shutdown()

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: VirtualGasMeterConfigEntry,
) -> None:
    """Reload a config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
