"""Sensor platform for Rotation Calibrator."""

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import DEGREE
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    ATTR_CALIBRATED,
    ATTR_DELTA,
    ATTR_MAX_ROTATION,
    ATTR_MIN_ROTATION,
    ATTR_REVERSE,
    CALIBRATION_OFFSET,
    CONF_INPUT_ENTITY,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    SW_VERSION,
)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: callable
):
    """Set up sensor platform."""
    input_entity = config_entry.data[CONF_INPUT_ENTITY]
    sensor = CalibratedRotationSensor(hass, config_entry, input_entity)
    async_add_entities([sensor])

    # Store sensor reference
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN][config_entry.entry_id] = {"sensor": sensor}


class CalibratedRotationSensor(RestoreEntity, SensorEntity):
    """Representation of a Calibrated Rotation Sensor."""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, input_entity: str
    ) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._config_entry = config_entry
        self._input_entity = input_entity
        self._state = None
        self._calibrating = False
        self._min = None
        self._max = None
        self._current_value = None
        self._reverse = False

    async def async_added_to_hass(self):
        """Register callbacks."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()
        if state:
            self._min = state.attributes.get(ATTR_MIN_ROTATION)
            self._max = state.attributes.get(ATTR_MAX_ROTATION)
            self._reverse = state.attributes.get(ATTR_REVERSE, False)

        async_track_state_change_event(
            self._hass, self._input_entity, self._async_input_changed
        )

    @callback
    def _async_input_changed(self, event: Event[EventStateChangedData]) -> None:
        """Handle input sensor changes."""
        new_state = event.data["new_state"]
        try:
            self._current_value = float(new_state.state)
        except (ValueError, TypeError):
            return

        if self._calibrating:
            self._update_min_max(self._current_value)

        self.async_write_ha_state()

    def _update_min_max(self, value):
        """Update min/max values during calibration."""
        if self._min is None or value < self._min:
            self._min = value
        if self._max is None or value > self._max:
            self._max = value

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._config_entry.data['name']} Calibrated Rotation"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._config_entry.entry_id}_sensor"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "name": self._config_entry.data["name"],
            "sw_version": SW_VERSION,
        }

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self._calibrating:
            return 0

        if None in (self._min, self._max, self._current_value):
            return 0

        # Pobierz encję number przez unique_id
        registry = er.async_get(self.hass)
        entity_id = registry.async_get_entity_id(
            "number", DOMAIN, f"{self._config_entry.entry_id}_config"
        )

        if not entity_id:
            return 0

        state = self.hass.states.get(entity_id)
        try:
            max_allowed = int(float(state.state)) if state else 100
        except (ValueError, TypeError):
            max_allowed = 100

        # Calculate with 5% offset
        input_range = self._max - self._min
        offset = input_range * CALIBRATION_OFFSET / 100
        calibrated_min = self._min + offset
        calibrated_max = self._max - offset

        if self._current_value <= calibrated_min:
            return max_allowed if self._reverse else 0
        if self._current_value >= calibrated_max:
            return 0 if self._reverse else max_allowed

        calculated_value = (
            (self._current_value - calibrated_min) / (calibrated_max - calibrated_min)
        ) * max_allowed

        return (
            round(max_allowed - calculated_value)
            if self._reverse
            else round(calculated_value)
        )

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        return {
            ATTR_MIN_ROTATION: self._min,
            ATTR_MAX_ROTATION: self._max,
            ATTR_DELTA: self._max - self._min
            if None not in (self._max, self._min)
            else None,
            ATTR_CALIBRATED: not self._calibrating
            and None not in (self._max, self._min),
            ATTR_REVERSE: self._reverse,
        }

    @property
    def state_class(self):
        """Return the state class."""
        return SensorStateClass.MEASUREMENT_ANGLE

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return DEGREE

    def start_calibration(self):
        """Start calibration process."""
        self._calibrating = True
        self._min = None
        self._max = None
        self.async_write_ha_state()

    def stop_calibration(self):
        """Stop calibration process."""
        self._calibrating = False
        self.async_write_ha_state()

    def set_reverse(self, value: bool):
        """Set reverse state."""
        self._reverse = value
        self.async_write_ha_state()

    @property
    def is_calibrating(self):
        """Return True if calibration is active."""
        return self._calibrating

    @property
    def is_reverse(self):
        """Return True if reverse is active."""
        return self._reverse
