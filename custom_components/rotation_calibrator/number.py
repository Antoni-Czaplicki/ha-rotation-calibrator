"""Number platform for Rotation Calibrator."""

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DEFAULT_MAX_VALUE, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: callable
):
    """Set up number platform."""
    number_entity = CalibrationConfigNumber(config_entry)
    async_add_entities([number_entity])


class CalibrationConfigNumber(NumberEntity, RestoreEntity):
    """Representation of a Configuration Number Entity."""

    def __init__(self, config_entry) -> None:
        """Initialize the number entity."""
        self._config_entry = config_entry
        self._value = DEFAULT_MAX_VALUE

    async def async_added_to_hass(self):
        """Restore state."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if state:
            self._value = float(state.state)

    @property
    def name(self):
        """Return the name of the number entity."""
        return f"{self._config_entry.data['name']} Max Value"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._config_entry.entry_id}_config"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
        }

    @property
    def native_value(self):
        """Return the current value."""
        return self._value

    @property
    def native_min_value(self):
        """Return the minimum value."""
        return 1

    @property
    def native_max_value(self):
        """Return the maximum value."""
        return 100

    @property
    def native_step(self):
        """Return the step."""
        return 1

    def set_native_value(self, value):
        """Update the current value."""
        self._value = value
        self.schedule_update_ha_state()
