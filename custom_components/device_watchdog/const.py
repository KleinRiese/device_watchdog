DOMAIN = "device_watchdog"

CONF_ENTITIES = "entities"
CONF_TIMEOUTS = "timeouts"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_TIMEOUT_MINUTES = 5
DEFAULT_SCAN_INTERVAL_MINUTES = 1

ATTR_FAILED_ENTITIES = "failed_entities"
ATTR_LAST_UPDATES = "last_updates"

SERVICE_FORCE_CHECK = "force_check"

PLATFORMS = ["binary_sensor", "sensor"]