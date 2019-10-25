"""Package to interact with Flume Sensor"""
import base64
from datetime import datetime, timedelta
import json
import logging
import pytz
import requests

LOGGER = logging.getLogger(__name__)

class FlumeAuth:
    """Get the Authentication Bearer, User ID and list of devices from Flume API."""

    def __init__(self, username, password, client_id, client_secret):
        """Initialize the data object."""
        self._username = username
        self._password = password
        self._client_id = client_id
        self._client_secret = client_secret
        self._token = self.get_token()
        self._user_id = self.get_userid()
        self._bearer = self.get_bearer()
        
    def get_token(self):
        """Return authorization token for session."""
        url = "https://api.flumetech.com/oauth/token"
        payload = (
            '{"grant_type":"password","client_id":"'
            + self._client_id
            + '","client_secret":"'
            + self._client_secret
            + '","username":"'
            + self._username
            + '","password":"'
            + self._password
            + '"}'
        )
        headers = {"content-type": "application/json"}

        response = requests.request("POST", url, data=payload, headers=headers)

        LOGGER.debug("Token Payload: %s", payload)
        LOGGER.debug("Token Response: %s", response.text)

        if response.status_code != 200:
            raise Exception(
                "Can't get token for user {}. Response code returned : {}".format(
                    self._username, response.status_code
                )
            )

        return json.loads(response.text)["data"]

    def get_userid(self):
        """Return User ID for authorized user."""
        json_token_data = self._token[0]
        return json.loads(
            base64.b64decode(json_token_data["access_token"].split(".")[1])
        )["user_id"]

    def get_bearer(self):
        """Return Bearer for Authorized session."""
        return self._token[0]["access_token"]

class FlumeDeviceList:
    def __init__(self, username, password, client_id, client_secret):
        """Initialize the data object."""
        self._username = username
        self._password = password
        self._client_id = client_id
        self._client_secret = client_secret

        flume_auth = FlumeAuth(username, password, client_id, client_secret)

        self._user_id = flume_auth._user_id
        self._bearer = flume_auth._bearer
        self.device_list = self.get_devices()
    
    def get_devices(self):
        """Return all available devices from Flume API."""
        url = "https://api.flumetech.com/users/" + str(self._user_id) + "/devices"
        querystring = {"user": "false", "location": "false"}
        headers = {"authorization": "Bearer " + self._bearer + ""}
        response = requests.request("GET", url, headers=headers, params=querystring)

        LOGGER.debug("get_devices Response: %s", response.text)

        if response.status_code != 200:
            raise Exception(
                "Impossible to retreive devices. Response code returned : {}".format(
                    response.status_code
                )
            )

        return json.loads(response.text)["data"]


class FlumeData:
    """Get the latest data and update the states."""

    def __init__(
        self,
        username,
        password,
        client_id,
        client_secret,
        device_id,
        time_zone,
        scan_interval,
    ):
        """Initialize the data object."""
        self._username = username
        self._device_id = device_id
        self._scan_interval = scan_interval
        self._time_zone = time_zone
        self.value = None

        flume_auth = FlumeAuth(username, password, client_id, client_secret)

        self._user_id = flume_auth._user_id
        self._bearer = flume_auth._bearer
        self.update()

    def update(self):
        """Return updated value for session."""
        query_array = []
        utc_now = pytz.utc.localize(datetime.utcnow())
        time_zone_now = utc_now.astimezone(pytz.timezone(self._time_zone))

        url = (
            "https://api.flumetech.com/users/"
            + str(self._user_id)
            + "/devices/"
            + str(self._device_id)
            + "/query"
        )
        
        """Query 1: Specified start / end time"""
        since_datetime = (time_zone_now - self._scan_interval).strftime(
                "%Y-%m-%d %H:%M:00"
            )
        until_datetime = time_zone_now.strftime("%Y-%m-%d %H:%M:00")
        query_1 = {
            "since_datetime": since_datetime,
            "until_datetime": until_datetime,
            "bucket": "MIN",
            "request_id": "update",
            "units": "GALLONS",
            }
        
        """Update dictionary"""
        query_array.append(query_1)
        query_dict = {
            "queries": [
                query_array
            ]
        }

        headers = {"authorization": "Bearer " + self._bearer + ""}
        response = requests.post(url, json=query_dict, headers=headers)

        LOGGER.debug("Update URL: %s", url)
        LOGGER.debug("Update headers: %s", headers)
        LOGGER.debug("Update query_dict: %s", query_dict)
        LOGGER.debug("Update Response: %s", response.text)
        
        if response.status_code != 200:
            raise Exception(
                "Can't update flume data for user id {}. Response code returned : {}".format(
                    self._username, response.status_code
                )
            )

        self.value = json.loads(response.text)["data"][0]["update"][0]["value"]
