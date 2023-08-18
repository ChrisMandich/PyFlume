"""Constants to support PyFlume."""
# Time-related constants
API_LIMIT = 60
DEFAULT_TIMEOUT = 30

# Operation constants
CONST_OPERATION = "SUM"
CONST_UNIT_OF_MEASUREMENT = "GALLONS"

# Base URL
API_BASE_URL = "https://api.flumetech.com"

# Endpoints
URL_OAUTH_TOKEN = f"{API_BASE_URL}/oauth/token"
API_QUERY_URL = f"{API_BASE_URL}/users/{{user_id}}/devices/{{device_id}}/query"
API_DEVICES_URL = f"{API_BASE_URL}/users/{{user_id}}/devices"
API_NOTIFICATIONS_URL = f"{API_BASE_URL}/users/{{user_id}}/notifications"
API_LEAK_URL = (
    f"{API_BASE_URL}/users/{{user_id}}/devices/{{device_id}}/leaks/active"
)
API_USAGE_URL = f"{API_BASE_URL}/users/{{user_id}}/usage-alerts"
