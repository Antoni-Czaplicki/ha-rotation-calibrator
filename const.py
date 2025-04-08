"""Constants for Rotation Calibrator."""

from homeassistant.const import Platform

DOMAIN = "rotation_calibrator"
PLATFORMS = [Platform.NUMBER, Platform.SENSOR, Platform.SWITCH]

# Device info
MANUFACTURER = "Antek"
MODEL = "Rotation Calibrator"
SW_VERSION = "1.0"

CONF_INPUT_ENTITY = "input_entity"
CALIBRATION_OFFSET = 5  # 5% offset on both ends

ATTR_MIN_ROTATION = "min_rotation"
ATTR_MAX_ROTATION = "max_rotation"
ATTR_DELTA = "delta"
ATTR_CALIBRATED = "calibrated"
ATTR_REVERSE = "reverse"

DEFAULT_MAX_VALUE = 100
