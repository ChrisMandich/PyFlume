# PyFlume
Authenticates to Flume API, returns a list of devices and allows you to pull the latest sensor results over a period of time.  

## Configuration
You can find your Client ID and Client Secret under "API Access" on the [settings page](https://https://portal.flumetech.com/#settings). 

## Configuration Variables
```
username:
  description: Your flume user id.
  required: true
  type: string
password:
  description: Your flume password.
  required: true
  type: string
client_id:
  description: Your flume Client ID.
  required: true
  type: string
client_secret:
  description: Your flume Client Secret.
  required: true
  type: string
```

## Examples

```
import pyflume
from datetime import timedelta
from requests import Session

KEY_DEVICE_TYPE = "type"
KEY_DEVICE_ID = "id"
FLUME_TYPE_SENSOR = 2

username="<username>"
password="<password>"
client_id="<client_id>"
client_secret="<client_secret>"

SCAN_INTERVAL = timedelta(minutes=60)

auth = pyflume.FlumeAuth(
        username, password, client_id, client_secret, http_session=Session()
        )

flume_devices = pyflume.FlumeDeviceList(auth)
devices = flume_devices.get_devices()

print("DEVICE LIST")
print(devices)

print("DEVICE ID")
for device in flume_devices.device_list:
    if device[KEY_DEVICE_TYPE] == FLUME_TYPE_SENSOR:
        print(device[KEY_DEVICE_ID])
        device_id = device[KEY_DEVICE_ID]

flume = pyflume.FlumeData(
            auth,
            device_id,
            SCAN_INTERVAL,
            http_session=Session(),
        )

flume_notifications = pyflume.FlumeNotificationList(auth, read="true")

print("NOTIFICATION LIST")
print(flume_notifications.notification_list)

## Force Update
flume.update_force()

print("AUTH HEADER")
print(auth.authorization_header)

print("QUERY PAYLOAD")
print(pyflume._generate_api_query_payload(SCAN_INTERVAL))

print("FLUME VALUES")
print(flume.values)
```
