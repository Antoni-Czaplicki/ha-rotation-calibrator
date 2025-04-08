"""Switch platform for Rotation Calibrator."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the calibration switch."""
    sensor = hass.data[DOMAIN][entry.entry_id]["sensor"]
    async_add_entities([CalibrationSwitch(entry, sensor), ReverseSwitch(entry, sensor)])


class CalibrationSwitch(SwitchEntity):
    """Representation of a Calibration Switch."""

    def __init__(self, config_entry: ConfigEntry, sensor) -> None:
        """Initialize the switch."""
        self._config_entry = config_entry
        self._sensor = sensor

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._config_entry.entry_id}_switch"

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return f"{self._config_entry.data['name']} Calibration"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
        }

    @property
    def is_on(self) -> bool:
        """Return True if calibration is active."""
        return self._sensor.is_calibrating

    async def async_turn_on(self, **kwargs):
        """Start calibration."""
        self._sensor.start_calibration()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Stop calibration."""
        self._sensor.stop_calibration()
        self.async_write_ha_state()


class ReverseSwitch(SwitchEntity):
    """Switch to reverse rotation direction."""

    def __init__(self, config_entry: ConfigEntry, sensor) -> None:
        """Initialize the switch."""
        self._config_entry = config_entry
        self._sensor = sensor

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._config_entry.entry_id}_reverse_switch"

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return f"{self._config_entry.data['name']} Reverse Direction"

    @property
    def icon(self) -> str:
        """Return the icon for the switch."""
        return "mdi:swap-horizontal"

    @property
    def is_on(self) -> bool:
        """Return True if reverse is active."""
        return self._sensor.is_reverse

    async def async_turn_on(self, **kwargs):
        """Enable reverse rotation."""
        self._sensor.set_reverse(True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Disable reverse rotation."""
        self._sensor.set_reverse(False)
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
        }
