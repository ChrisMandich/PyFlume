"""Package to interact with Flume Sensor."""
import json
import logging
from datetime import datetime, timedelta
from os import path
from tempfile import gettempdir

import jwt  # pyjwt
import pytz
import requests
from ratelimit import limits, sleep_and_retry


URL_OAUTH_TOKEN = "https://api.flumetech.com/oauth/token"
TOKEN_FILE = path.join(gettempdir(), "FLUME_TOKEN_FILE")
API_LIMIT = 60

LOGGER = logging.getLogger(__name__)


def _response_error(message, response):
    if response.status_code == 400:
        error_message = json.loads(response.text)["detailed"][0]
    if response.status_code != 200:
        error_message = json.loads(response.text)["message"]
    raise Exception(
        f'''Message:{message}.
            Response code returned:{response.status_code}.
            Eror message returned:{error_message}.'''
    )


class FlumeAuth:
    """Interact with API Authentication."""

    def __init__(
            self,
            username,
            password,
            client_id,
            client_secret,
            flume_token_file=TOKEN_FILE,):
        """Initialize the data object."""
        self._creds = {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "username": username,
                        "password": password
                        }
        self._token_file = flume_token_file
        self._token = None
        self._decoded_token = None
        self.user_id = None
        self.authorization_header = None

        self.read_token_file()

    def token_request(self, payload):
        """Request Authorization Payload."""
        headers = {"content-type": "application/json"}
        response = requests.request(
            "POST",
            URL_OAUTH_TOKEN,
            json=payload,
            headers=headers
            )

        LOGGER.debug("Token Payload: %s", payload)
        LOGGER.debug("Token Response: %s", response.text)

        # Check for response errors.
        _response_error(
            f"Can't get token for user {self._creds['username']}",
            response
            )

        return json.loads(response.text)["data"][0]

    def fetch_token(self):
        """Return authorization token for session."""
        payload = dict({"grant_type": "password"}, **self._creds)
        self.load_token(self.token_request(payload))
        self.write_token_file()

    def refresh_token(self):
        """Return authorization token for session."""
        payload = {
                        "grant_type": "refresh_token",
                        "refresh_token": self._token['refresh_token'],
                        "client_id": self._creds['client_id'],
                        "client_secret": self._creds['client_secret']
                }
        self.load_token(self.token_request(payload))
        self.write_token_file()

    def verify_token(self):
        """Check to see if token is expiring in 12 hours."""
        token_expiration = datetime.fromtimestamp(self._decoded_token['exp'])
        time_difference = datetime.now() + timedelta(hours=12)

        LOGGER.debug("Token expiration time: %s", token_expiration)
        LOGGER.debug("Token comparison time: %s", time_difference)

        if token_expiration <= time_difference:
            self.refresh_token()

    def load_token(self, token):
        """Update _token, decode token, user_id and auth header."""
        self._token = token
        try:
            self._decoded_token = jwt.decode(
                self._token['access_token'],
                verify=False
                )
        except jwt.exceptions.DecodeError:
            LOGGER.debug("Poorly formatted Access Token, \
            fetching token using _creds")

            self.fetch_token()

        self.user_id = self._decoded_token['user_id']
        self.authorization_header = {
            "authorization": "Bearer " + self._token['access_token']
            }

    def write_token_file(self):
        """Write token locally."""
        with open(self._token_file, 'w') as token_file:
            token_file.write(json.dumps(self._token))

    def read_token_file(self):
        """Read local token file and load it."""
        try:
            with open(self._token_file, 'r') as token_file:
                self.load_token(json.load(token_file))
            self.verify_token()
        except FileNotFoundError:
            LOGGER.debug("Token file does not exist, \
            fetching token using _creds")
            self.fetch_token()
            self.write_token_file()
        except json.decoder.JSONDecodeError:
            LOGGER.debug("Invalid JSON in token file, \
            fetching token using _creds")
            self.fetch_token()
            self.write_token_file()


class FlumeDeviceList:
    """Get Flume Device List from API."""

    def __init__(
            self,
            username,
            password,
            client_id,
            client_secret,
            flume_token_file=TOKEN_FILE,):
        """Initialize the data object."""
        self._flume_auth = FlumeAuth(
            username,
            password,
            client_id,
            client_secret,
            flume_token_file
            )
        self.device_list = self.get_devices()

    def get_devices(self):
        """Return all available devices from Flume API."""
        url = f"https://api.flumetech.com/users/\
        {self._flume_auth.user_id}/devices"

        querystring = {"user": "false", "location": "false"}
        response = requests.request(
            "GET",
            url,
            headers=self._flume_auth.authorization_header,
            params=querystring
            )

        LOGGER.debug("get_devices Response: %s", response.text)

        # Check for response errors.
        _response_error("Impossible to retreive devices", response)

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
            flume_token_file=TOKEN_FILE,):
        """Initialize the data object."""
        self._flume_auth = FlumeAuth(
            username,
            password,
            client_id,
            client_secret,
            flume_token_file
            )
        self._scan_interval = scan_interval
        self._time_zone = time_zone
        self.device_id = device_id
        self.value = None

        self.update()

    @sleep_and_retry
    @limits(calls=2, period=API_LIMIT)
    def update(self):
        """Return updated value for session."""
        query_array = []
        utc_now = pytz.utc.localize(datetime.utcnow())
        time_zone_now = utc_now.astimezone(pytz.timezone(self._time_zone))
        self._flume_auth.read_token_file()

        url = f"https://api.flumetech.com/users/{self._flume_auth.user_id}\
        /devices/{self.device_id}/query"

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

        query_array.append(query_1)
        query_dict = {
            "queries": query_array
        }

        response = requests.post(
            url,
            json=query_dict,
            headers=self._flume_auth.authorization_header
            )

        LOGGER.debug("Update URL: %s", url)
        LOGGER.debug("Update query_dict: %s", query_dict)
        LOGGER.debug("Update Response: %s", response.text)

        # Check for response errors.
        _response_error(f"Can't update flume data for user id \
        {self._flume_auth.user_id}", response)
        self.value = json.loads(response.text)["data"][0]["update"][0]["value"]
