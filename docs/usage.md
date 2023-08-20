# FlumeUsageAlertList
## Overview
FlumeUsageAlertList is a Python class designed to retrieve usage alert notifications from the Flume API. This class enables querying of usage alerts from devices owned by the user and provides control over the state of the usage alert list (read or not read).

## Dependencies
 - requests

## Initialization
To initialize the FlumeUsageAlertList object, you'll need the following parameters:

 - `flume_auth`: FlumeAuth object for authentication.
 - `http_session`: (Optional) Requests Session() object.
 - `timeout`: (Optional) Requests timeout for throttling. The default value is specified in DEFAULT_TIMEOUT.
 - `read`: (Optional) State of usage alert list; specifies if they have been read or not read. Default is "false."

## Methods
Usage Alert Retrieval

`get_usage_alerts()`
Method to return all usage alerts from devices owned by the user. This method fetches a JSON list containing the usage alerts.

`get_next_usage_alerts()`
Method to return the next page of usage alerts from devices owned by the user. This method fetches a JSON list containing the usage alerts for the next page.

Raises:
 - `ValueError`: If no next page is available.

`_has_next_page(response_json)`
Returns True if the next page exists. Used internally to handle pagination.

`_get_usage_request(api_url, query_string)`
Makes an API request to get usage alerts from the Flume API.

## Example
```python
import pyflume
auth = pyflume.FlumeAuth(
    username='your_username',
    password='your_password',
    client_id='client_id',
    client_secret='client_secret'
)
auth.retrieve_token()

usage_alert_list_obj = pyflume.FlumeUsageAlertList(
    flume_auth=auth
)
usage_alert_list = usage_alert_list_obj.get_usage_alerts()
print(usage_alert_list)  # Prints the JSON list of usage alerts
```

For subsequent pages:
```python
if usage_alert_list_obj.has_next:
    next_page_alerts = usage_alert_list_obj.get_next_usage_alerts()
    print(next_page_alerts)  # Prints the JSON list of usage alerts for the next page
```