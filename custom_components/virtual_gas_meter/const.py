"""Constants for Virtual Gas Meter."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "virtual_gas_meter"
ATTRIBUTION = "Calculated by Virtual Gas Meter"
PARALLEL_UPDATES = 1

CONF_BOILER_ENTITY = "boiler_entity_id"
CONF_UNIT = "unit"
CONF_INITIAL_METER_READING = "initial_meter_reading"
CONF_INITIAL_AVERAGE_RATE = "initial_average_rate"
CONF_AVERAGE_RATE = "average_rate_per_h"

UNIT_M3 = "m3"
UNIT_CCF = "CCF"
UNIT_OPTIONS = [UNIT_M3, UNIT_CCF]

ALLOWED_BOILER_DOMAINS = ["switch", "climate", "binary_sensor", "sensor"]

STORAGE_VERSION = 1
STORAGE_KEY = "virtual_gas_meter_v3"

SERVICE_REAL_METER_READING_UPDATE = "real_meter_reading_update"

ATTR_METER_READING = "meter_reading"
ATTR_TIMESTAMP = "timestamp"
ATTR_RECALCULATE_AVERAGE_RATE = "recalculate_average_rate"

DEVICE_NAME = "Virtual Gas Meter"
DEVICE_MANUFACTURER = "Virtual Gas Meter"
DEVICE_MODEL = "Gas Usage Estimator"

SENSOR_VIRTUAL_GAS_METER_TOTAL = "vgm_gas_meter_total"
SENSOR_CONSUMED_GAS = "vgm_consumed_gas"
SENSOR_HEATING_INTERVAL = "vgm_heating_interval"

DEFAULT_ENTITY_ID_TOTAL = "sensor.vgm_total"
DEFAULT_ENTITY_ID_CONSUMED_GAS = "sensor.vgm_consumed_gas"
DEFAULT_ENTITY_ID_HEATING_INTERVAL = "sensor.vgm_heating_interval"

DATA_METER_TOTAL = "meter_total"
DATA_CONSUMED_GAS = "consumed_gas"
DATA_HEATING_INTERVAL = "heating_interval"

UPDATE_INTERVAL_SECONDS = 60
MINUTES_PER_HOUR = 60
DECIMAL_PLACES = 3
