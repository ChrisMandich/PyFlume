# FlumeLeakList
## Overview
FlumeLeakList is a Python class designed to retrieve leak notifications from the Flume API. The class can query leak alerts for specific devices and provides control over the state of the notification list (read or not read).

## Dependencies
 - requests

## Initialization
To initialize the FlumeLeakList object, you'll need the following parameters:

 - `flume_auth`: FlumeAuth object for authentication.
 - `device_id`: The Device ID to query.
 - `http_session`: (Optional) Requests Session() object.
 - `timeout`: (Optional) Requests timeout for throttling. The default value is specified in DEFAULT_TIMEOUT.
 - `read`: (Optional) State of leak notification list; specifies if they have been read or not read. Default is "false."

## Methods
Leak Notification Retrieval

`get_leaks()`
Method to return all leak alerts from devices owned by the user. This method fetches the JSON list of leak notifications, sorted in ascending order.

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

leak_list_obj = pyflume.FlumeLeakList(
    flume_auth=auth,
    device_id='your_device_id'
)
leak_alert_list = leak_list_obj.get_leaks()
print(leak_alert_list)  # Prints the JSON list of leak notifications
```