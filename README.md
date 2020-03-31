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
## Retrieve a list of devices: 
```
import pyflume

flume_devices = pyflume.FlumeDeviceList(username, password, client_id, client_secret)`
```

## Return Data for all Flume Devices of Type 2

```
import pyflume
from datetime import timedelta

username="<username>"
password="<password>"
client_id="<client_id>"
client_secret="<client_secret>"

flume_auth = pyflume.FlumeAuth(username, password, client_id, client_secret)

flume_devices = pyflume.FlumeDeviceList(flume_auth)

SCAN_INTERVAL = timedelta(minutes=1) # Using datetime

for device in flume_devices.device_list:
    if device["type"] == 2:
        flume = pyflume.FlumeData(
            flume_auth,
            device["id"],
            SCAN_INTERVAL,
        )
```
