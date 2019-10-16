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
flume_devices = FlumeAuth(username, password, client_id, client_secret)`
```

## Return Data for all Flume Devices of Type 2

```
SCAN_INTERVAL = timedelta(minutes=1) # Using datetime
TIME_ZONE='America/Los_Angeles' # Using pytz

for device in flume_devices.device_list:
    if device["type"] == 2:
        flume = FlumeData(
            username,
            password,
            client_id,
            client_secret,
            device["id"],
            TIME_ZONE,
            SCAN_INTERVAL,
        )
```
