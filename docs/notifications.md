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

`get_next_notifications()`
Method to return the next page of notifications from devices owned by the user. Raises a ValueError if no next page is available.

Raises:
 - `ValueError`: If no next page is available.

`_has_next_page(response_json)`
Returns True if the next page exists. Used internally to handle pagination.

`_get_notification_request(api_url, query_string)`
Make an API request to get usage alerts from the Flume API.

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

notification_list_obj = pyflume.FlumeNotificationList(
    flume_auth=auth
)
notification_list = notification_list_obj.get_notifications()
print(notification_list)  # Prints the JSON dictionary of notifications
```

For subsequent pages:
```python
if notification_list_obj.has_next:
    next_page_notifications = notification_list_obj.get_next_notifications()
    print(next_page_notifications)  # Prints the JSON list of notifications for the next page
```