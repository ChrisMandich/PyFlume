# FlumeDeviceList
## Overview
FlumeDeviceList is a Python class designed to retrieve the Flume device list from the Flume API. It leverages the authentication handled by FlumeAuth and provides an interface to access the list of devices associated with the user account.

## Dependencies
 - requests

## Initialization
To initialize the FlumeDeviceList object, you'll need the following parameters:

 - `flume_auth`: FlumeAuth object for authentication.
 - `http_session`: (Optional) Requests Session() object.
 - `timeout`: (Optional) Requests timeout for throttling. The default value is specified in DEFAULT_TIMEOUT.

## Methods
Device Retrieval

`get_devices()`
Method to return all available devices from the Flume API. This method fetches the JSON device list.

Example
```python
auth = FlumeAuth(
    username='your_username',
    password='your_password',
    client_id='client_id',
    client_secret='client_secret'
)
auth.retrieve_token()

device_list_obj = FlumeDeviceList(
    flume_auth=auth
)
device_list = device_list_obj.get_devices()
print(device_list)  # Prints the JSON device list
```