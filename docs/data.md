# FlumeData
## Overview
FlumeData is a Python class responsible for retrieving and updating data from the Flume API. It works in tandem with the FlumeAuth class for authentication and provides an interface to interact with various Flume data endpoints.

## Dependencies
 - ratelimit
 - requests
 - Python ≥ 3.9 or the backports.zoneinfo package for earlier versions.

## Initialization
To initialize the FlumeData object, you'll need the following parameters:

 - `flume_auth`: FlumeAuth object for authentication.
 - `device_id`: Flume device id.
 - `device_tz`: Timezone of the device.
 - `scan_interval`: Duration of the scan (e.g., 60 minutes).
 - `update_on_init`: (Optional) Whether to update on initialization. Default is True.
 - `http_session`: (Optional) Requests Session() object.
 - `timeout`: (Optional) Requests timeout for throttling. Default value is specified in DEFAULT_TIMEOUT.
 - `query_payload`: (Optional) Specific query payload to request for the device.

## Methods
Update Methods

`update()`
Method to return updated values for the session. Adheres to API call limits.

`update_force()`
Method to return updated values for the session without auto-retry or limits.

## Internals
There are also some internal methods that handle the generation of the API query payload and other functionalities. Most users will not need to interact with these directly.

## Example
```python
auth = FlumeAuth(
    username='your_username',
    password='your_password',
    client_id='client_id',
    client_secret='client_secret'
)
auth.retrieve_token()

data = FlumeData(
    flume_auth=auth,
    device_id='your_device_id',
    device_tz='your_timezone',
    scan_interval=timedelta(minutes=60)
)
data.update()
print(data.values)  # Prints the current data values
```
