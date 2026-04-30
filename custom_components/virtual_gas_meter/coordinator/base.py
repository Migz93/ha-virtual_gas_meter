"""Coordinator for Virtual Gas Meter calculations."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from logging import Logger
from typing import Any

import voluptuous as vol

from custom_components.virtual_gas_meter.const import (
    ATTR_METER_READING,
    ATTR_RECALCULATE_AVERAGE_RATE,
    ATTR_TIMESTAMP,
    CONF_BOILER_ENTITY,
    CONF_INITIAL_AVERAGE_RATE,
    CONF_INITIAL_METER_READING,
    CONF_UNIT,
    DATA_CONSUMED_GAS,
    DATA_HEATING_INTERVAL,
    DATA_METER_TOTAL,
    DECIMAL_PLACES,
    DOMAIN,
    MINUTES_PER_HOUR,
    STORAGE_KEY,
    STORAGE_VERSION,
    UPDATE_INTERVAL_SECONDS,
)
from custom_components.virtual_gas_meter.data import VirtualGasMeterConfigEntry, VirtualGasMeterState
from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

type VirtualGasMeterData = dict[str, Any]


class VirtualGasMeterDataUpdateCoordinator(DataUpdateCoordinator[VirtualGasMeterData]):
    """Manage Virtual Gas Meter runtime state and entity updates."""

    config_entry: VirtualGasMeterConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        logger: Logger,
        config_entry: VirtualGasMeterConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=None,
            always_update=True,
        )
        self._store: Store[dict[str, Any]] = Store(
            hass,
            STORAGE_VERSION,
            f"{STORAGE_KEY}_{config_entry.entry_id}",
        )
        self._boiler_entity_id = config_entry.data[CONF_BOILER_ENTITY]
        self._unit = config_entry.data[CONF_UNIT]
        self._state = VirtualGasMeterState(
            last_real_meter_reading=config_entry.data[CONF_INITIAL_METER_READING],
            last_real_meter_timestamp=dt_util.now(),
            average_rate_per_h=config_entry.data[CONF_INITIAL_AVERAGE_RATE],
            consumed_gas=0.0,
            heating_interval_minutes=0,
        )
        self._boiler_last_state: str | None = None
        self._unsub_boiler_listener: Callable[[], None] | None = None
        self._unsub_interval_listener: Callable[[], None] | None = None

    async def _async_setup(self) -> None:
        """Load persisted data and subscribe to boiler state changes."""
        await self._load_data()

        self._unsub_boiler_listener = async_track_state_change_event(
            self.hass,
            [self._boiler_entity_id],
            self._handle_boiler_state_change,
        )
        self._unsub_interval_listener = async_track_time_interval(
            self.hass,
            self._handle_interval_update,
            timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )

        state = self.hass.states.get(self._boiler_entity_id)
        if state is not None:
            self._boiler_last_state = self._get_boiler_state(state.state)

    async def _async_update_data(self) -> VirtualGasMeterData:
        """Return the current calculated data snapshot."""
        return self._data_snapshot()

    async def async_shutdown(self) -> None:
        """Unload listeners and persist current data."""
        if self._unsub_boiler_listener is not None:
            self._unsub_boiler_listener()
            self._unsub_boiler_listener = None

        if self._unsub_interval_listener is not None:
            self._unsub_interval_listener()
            self._unsub_interval_listener = None

        await self._save_data()

    async def async_save_data(self) -> None:
        """Persist runtime state."""
        await self._save_data()

    @property
    def unit(self) -> str:
        """Return the configured unit."""
        return self._unit

    @property
    def boiler_entity_id(self) -> str:
        """Return the tracked boiler entity ID."""
        return self._boiler_entity_id

    @property
    def state(self) -> VirtualGasMeterState:
        """Return the current runtime state."""
        return self._state

    def get_heating_interval_string(self) -> str:
        """Return the heating interval as a display string."""
        hours = self._state.heating_interval_minutes // MINUTES_PER_HOUR
        minutes = self._state.heating_interval_minutes % MINUTES_PER_HOUR
        return f"{hours}h {minutes}m"

    async def async_handle_real_meter_reading_update(self, call: ServiceCall) -> None:
        """Handle a real meter reading update service call."""
        meter_reading = call.data[ATTR_METER_READING]
        timestamp = call.data.get(ATTR_TIMESTAMP, dt_util.now())
        recalculate = call.data.get(ATTR_RECALCULATE_AVERAGE_RATE, True)

        if meter_reading < self._state.last_real_meter_reading:
            msg = (
                f"New meter reading ({meter_reading:.{DECIMAL_PLACES}f}) is less than the previous reading "
                f"({self._state.last_real_meter_reading:.{DECIMAL_PLACES}f})"
            )
            raise HomeAssistantError(msg)

        old_reading = self._state.last_real_meter_reading
        runtime_minutes = self._state.heating_interval_minutes
        runtime_hours = runtime_minutes / MINUTES_PER_HOUR

        if runtime_minutes > 0 and recalculate:
            actual_used = meter_reading - self._state.last_real_meter_reading
            self._state.average_rate_per_h = actual_used / runtime_hours

            self.logger.info(
                "Real meter reading update: reading=%.3f -> %.3f, runtime=%dm (%.2fh), "
                "actual_used=%.3f, new_rate=%.3f %s/h",
                old_reading,
                meter_reading,
                runtime_minutes,
                runtime_hours,
                actual_used,
                self._state.average_rate_per_h,
                self._unit,
            )
        elif runtime_minutes > 0:
            self.logger.info(
                "Real meter reading update without rate recalculation: reading=%.3f -> %.3f, runtime=%dm",
                old_reading,
                meter_reading,
                runtime_minutes,
            )
        else:
            self.logger.info(
                "Real meter reading update with no runtime: reading=%.3f -> %.3f",
                old_reading,
                meter_reading,
            )

        self._state.last_real_meter_reading = meter_reading
        self._state.last_real_meter_timestamp = timestamp
        self._state.consumed_gas = 0.0
        self._state.heating_interval_minutes = 0

        self.async_set_updated_data(self._data_snapshot())
        await self._save_data()

    def _data_snapshot(self) -> VirtualGasMeterData:
        """Return a rounded snapshot for entity consumption."""
        return {
            DATA_METER_TOTAL: round(self._state.meter_total, DECIMAL_PLACES),
            DATA_CONSUMED_GAS: round(self._state.consumed_gas, DECIMAL_PLACES),
            DATA_HEATING_INTERVAL: self.get_heating_interval_string(),
        }

    def _get_boiler_state(self, state_str: str) -> str:
        """Return ``on`` when the configured boiler entity is heating."""
        if state_str in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return "off"

        entity_domain = self._boiler_entity_id.split(".", maxsplit=1)[0]

        if entity_domain == "climate":
            state_obj = self.hass.states.get(self._boiler_entity_id)
            if state_obj is not None and state_obj.attributes.get("hvac_action") == "heating":
                return "on"
            return "off"

        if entity_domain in ("switch", "binary_sensor"):
            return "on" if state_str == STATE_ON else "off"

        if entity_domain == "sensor":
            try:
                return "on" if float(state_str) > 0 else "off"
            except TypeError, ValueError:
                return "on" if state_str.lower() == STATE_ON else "off"

        return "off"

    @callback
    def _handle_boiler_state_change(self, event: Event[EventStateChangedData]) -> None:
        """Handle boiler state changes."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        current_boiler_state = self._get_boiler_state(new_state.state)

        self.logger.debug(
            "Boiler state change: %s -> %s",
            self._boiler_last_state,
            current_boiler_state,
        )

        if self._boiler_last_state == "on" and current_boiler_state == "off":
            self._perform_tick()

        self._boiler_last_state = current_boiler_state

    @callback
    def _handle_interval_update(self, now: datetime) -> None:
        """Handle the one-minute runtime interval."""
        if self._boiler_last_state == "on":
            self._perform_tick()

    def _perform_tick(self) -> None:
        """Add one minute of estimated boiler consumption."""
        self._state.heating_interval_minutes += 1
        self._state.consumed_gas += self._state.average_rate_per_h / MINUTES_PER_HOUR

        self.logger.debug(
            "Runtime tick: interval=%s, consumed=%.3f, meter_total=%.3f",
            self.get_heating_interval_string(),
            self._state.consumed_gas,
            self._state.meter_total,
        )

        self.async_set_updated_data(self._data_snapshot())
        self.config_entry.async_create_background_task(
            self.hass,
            self._save_data(),
            "save virtual gas meter data",
        )

    async def _load_data(self) -> None:
        """Load persisted data from V3-compatible storage."""
        data = await self._store.async_load()
        if not data:
            return

        self._state.last_real_meter_reading = vol.Coerce(float)(
            data.get("last_real_meter_reading", self._state.last_real_meter_reading),
        )
        self._state.last_real_meter_timestamp = datetime.fromisoformat(
            data.get("last_real_meter_timestamp", self._state.last_real_meter_timestamp.isoformat()),
        )
        self._state.average_rate_per_h = vol.Coerce(float)(
            data.get("average_rate_per_h", self._state.average_rate_per_h),
        )
        self._state.consumed_gas = vol.Coerce(float)(data.get("consumed_gas", 0.0))
        self._state.heating_interval_minutes = vol.Coerce(int)(data.get("heating_interval_minutes", 0))

        self.logger.debug(
            "Loaded persisted data: last_reading=%.3f, consumed=%.3f, interval=%dm, rate=%.3f",
            self._state.last_real_meter_reading,
            self._state.consumed_gas,
            self._state.heating_interval_minutes,
            self._state.average_rate_per_h,
        )

    async def _save_data(self) -> None:
        """Save V3-compatible runtime data."""
        await self._store.async_save(
            {
                "last_real_meter_reading": self._state.last_real_meter_reading,
                "last_real_meter_timestamp": self._state.last_real_meter_timestamp.isoformat(),
                "average_rate_per_h": self._state.average_rate_per_h,
                "consumed_gas": self._state.consumed_gas,
                "heating_interval_minutes": self._state.heating_interval_minutes,
            },
        )
