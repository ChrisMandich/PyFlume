# FlumeNotificationList
## Overview
FlumeNotificationList is a Python class for retrieving notifications from the Flume API. This class allows querying of notifications from devices owned by the user and provides control over the state of the notification list (read or not read).

## Dependencies
 - requests

## Initialization
To initialize the FlumeNotificationList object, you'll need the following parameters:

 - `flume_auth`: FlumeAuth object for authentication.
 - `http_session`: (Optional) Requests Session() object.
 - `timeout`: (Optional) Requests timeout for throttling. The default value is specified in DEFAULT_TIMEOUT.
 - `read`: (Optional) State of notification list; specifies if they have been read or not read. Default is "false."

## Methods
Notification Retrieval

`get_notifications()`
Method to return all notifications from devices owned by the user. This method fetches a JSON dictionary containing the notification messages.

## Example
```python 
auth = FlumeAuth(
    username='your_username',
    password='your_password',
    client_id='client_id',
    client_secret='client_secret'
)
auth.retrieve_token()

notification_list_obj = FlumeNotificationList(
    flume_auth=auth
)
notification_list = notification_list_obj.get_notifications()
print(notification_list)  # Prints the JSON dictionary of notifications
```