"""Package to interact with Flume Sensor."""

from datetime import datetime, timedelta
import json
import logging
from os import path
from tempfile import gettempdir

import jwt  # pip install pyjwt
import pytz
from ratelimit import limits, sleep_and_retry
from requests import Session

TOKEN_FILE = path.join(gettempdir(), "FLUME_TOKEN_FILE")
API_LIMIT = 60

DEFAULT_TIMEOUT = 30

API_BASE_URL = "https://api.flumetech.com"
URL_OAUTH_TOKEN = API_BASE_URL + "/oauth/token"
API_QUERY_URL = API_BASE_URL + "/users/{user_id}/devices/{device_id}/query"
API_DEVICES_URL = API_BASE_URL + "/users/{user_id}/devices"
API_NOTIFICATIONS_URL = API_BASE_URL + "/users/{user_id}/notifications"

LOGGER = logging.getLogger(__name__)


def _generate_api_query_payload(scan_interval):
    datetime_today = pytz.utc.localize(datetime.utcnow())

    def format_time(time):
        return time.strftime("%Y-%m-%d %H:%M:00")

    def format_start_today():
        return format_time(datetime.combine(datetime_today, datetime.min.time()))

    def format_start_month():
        return format_time(
            datetime.combine(datetime_today.replace(day=1), datetime.min.time())
        )

    def format_start_week():
        return format_time(
            datetime.combine(
                datetime_today - timedelta(days=datetime_today.weekday()),
                datetime.min.time(),
            )
        )

    queries = [
        {
            "request_id": "current_interval",
            "bucket": "MIN",
            "since_datetime": format_time(
                (datetime_today - scan_interval).replace(second=0)
            ),
            "until_datetime": format_time(datetime_today.replace(second=0)),
            "operation": "SUM",
            "units": "GALLONS",
            "tz": "UTC",
        },
        {
            "request_id": "today",
            "bucket": "DAY",
            "since_datetime": format_start_today(),
            "until_datetime": format_time(datetime_today),
            "operation": "SUM",
            "units": "GALLONS",
            "tz": "UTC",
        },
        {
            "request_id": "week_to_date",
            "bucket": "DAY",
            "since_datetime": format_start_week(),
            "until_datetime": format_time(datetime_today),
            "operation": "SUM",
            "units": "GALLONS",
            "tz": "UTC",
        },
        {
            "request_id": "month_to_date",
            "bucket": "MON",
            "since_datetime": format_start_month(),
            "until_datetime": format_time(datetime_today),
            "units": "GALLONS",
            "tz": "UTC",
        },
        {
            "request_id": "last_60_min",
            "bucket": "MIN",
            "since_datetime": format_time(datetime_today - timedelta(minutes=60)),
            "until_datetime": format_time(datetime_today),
            "operation": "SUM",
            "units": "GALLONS",
            "tz": "UTC",
        },
        {
            "request_id": "last_24_hrs",
            "bucket": "HR",
            "since_datetime": format_time(datetime_today - timedelta(hours=24)),
            "until_datetime": format_time(datetime_today),
            "operation": "SUM",
            "units": "GALLONS",
            "tz": "UTC",
        },
        {
            "request_id": "last_30_days",
            "bucket": "DAY",
            "since_datetime": format_time(datetime_today - timedelta(days=30)),
            "until_datetime": format_time(datetime_today),
            "operation": "SUM",
            "units": "GALLONS",
            "tz": "UTC",
        },
    ]
    return {"queries": queries}


def _response_error(message, response):
    if response.status_code == 200:
        return

    if response.status_code == 400:
        error_message = json.loads(response.text)["detailed"][0]
    else:
        error_message = json.loads(response.text)["message"]

    raise Exception(
        f"""Message:{message}.
            Response code returned:{response.status_code}.
            Eror message returned:{error_message}."""
    )


class FlumeAuth:
    """Interact with API Authentication."""

    def __init__(
        self,
        username,
        password,
        client_id,
        client_secret,
        flume_token_file=TOKEN_FILE,
        http_session: Session = Session(),
        timeout=DEFAULT_TIMEOUT,
    ):
        """Initialize the data object."""

        self._creds = {
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password,
        }

        self._http_session = http_session
        self._timeout = timeout
        self._token_file = flume_token_file
        self._token = None
        self._decoded_token = None
        self.user_id = None
        self.authorization_header = None
        self.read_token_file()

    def token_request(self, payload):
        """Request Authorization Payload."""

        headers = {"content-type": "application/json"}
        response = self._http_session.request(
            "POST",
            URL_OAUTH_TOKEN,
            json=payload,
            headers=headers,
            timeout=self._timeout,
        )

        LOGGER.debug("Token Payload: %s", payload)
        LOGGER.debug("Token Response: %s", response.text)

        # Check for response errors.
        _response_error(f"Can't get token for user {self._creds['username']}", response)

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
            "refresh_token": self._token["refresh_token"],
            "client_id": self._creds["client_id"],
            "client_secret": self._creds["client_secret"],
        }

        self.load_token(self.token_request(payload))
        self.write_token_file()

    def verify_token(self):
        """Check to see if token is expiring in 12 hours."""
        token_expiration = datetime.fromtimestamp(self._decoded_token["exp"])
        time_difference = datetime.now() + timedelta(hours=12)
        LOGGER.debug("Token expiration time: %s", token_expiration)
        LOGGER.debug("Token comparison time: %s", time_difference)

        if token_expiration <= time_difference:
            self.refresh_token()

    def load_token(self, token):
        """Update _token, decode token, user_id and auth header."""

        self._token = token
        try:
            self._decoded_token = jwt.decode(self._token["access_token"], verify=False)
        except jwt.exceptions.DecodeError:
            LOGGER.debug("Poorly formatted Access Token, fetching token using _creds")
            self.fetch_token()

        self.user_id = self._decoded_token["user_id"]

        self.authorization_header = {
            "authorization": "Bearer " + self._token["access_token"]
        }

    def write_token_file(self):
        """Write token locally."""
        with open(self._token_file, "w") as token_file:
            token_file.write(json.dumps(self._token))

    def _read_token_file(self):
        """Read local token file and load it."""
        with open(self._token_file, "r") as token_file:
            self.load_token(json.load(token_file))

    def read_token_file(self):
        """Read local token file and load it."""
        try:
            if not self._decoded_token:
                # Only re-read from disk if we do not already
                # have the token in memory
                self._read_token_file()
            self.verify_token()
        except FileNotFoundError:
            LOGGER.debug("Token file does not exist, fetching token using _creds")
            self.fetch_token()
            self.write_token_file()
        except json.decoder.JSONDecodeError:
            LOGGER.debug("Invalid JSON in token file, fetching token using _creds")
            self.fetch_token()
            self.write_token_file()


class FlumeDeviceList:
    """Get Flume Device List from API."""

    def __init__(
        self, flume_auth, http_session: Session = Session(), timeout=DEFAULT_TIMEOUT,
    ):
        """Initialize the data object."""
        self._timeout = timeout
        self._http_session = http_session
        self._flume_auth = flume_auth
        self.device_list = self.get_devices()

    def get_devices(self):
        """Return all available devices from Flume API."""

        url = API_DEVICES_URL.format(user_id=self._flume_auth.user_id)
        query_string = {"user": "true", "location": "true"}

        response = self._http_session.request(
            "GET",
            url,
            headers=self._flume_auth.authorization_header,
            params=query_string,
            timeout=self._timeout,
        )

        LOGGER.debug("get_devices Response: %s", response.text)

        # Check for response errors.
        _response_error("Impossible to retreive devices", response)

        return response.json()["data"]


class FlumeNotificationList:
    """Get Flume Notifications list from API."""

    def __init__(
        self,
        flume_auth,
        http_session: Session = Session(),
        timeout=DEFAULT_TIMEOUT,
        read="false",
    ):
        """Initialize the data object."""
        self._timeout = timeout
        self._http_session = http_session
        self._flume_auth = flume_auth
        self._read = read
        self.notification_list = self.get_notifications()

    def get_notifications(self):
        """Return all notifications from devices owned by the user"""

        url = API_NOTIFICATIONS_URL.format(user_id=self._flume_auth.user_id)

        query_string = {
            "limit": "50",
            "offset": "0",
            "sort_direction": "ASC",
            "read": self._read,
        }

        response = self._http_session.request(
            "GET",
            url,
            headers=self._flume_auth.authorization_header,
            params=query_string,
            timeout=self._timeout,
        )

        LOGGER.debug("get_notifications Response: %s", response.text)

        # Check for response errors.
        _response_error("Impossible to retrieve notifications", response)
        print(json.dumps(response.json()))
        return response.json()["data"]


class FlumeData:
    """Get the latest data and update the states."""

    def __init__(
        self,
        flume_auth,
        device_id,
        scan_interval,
        update_on_init=True,
        http_session: Session = Session(),
        timeout=DEFAULT_TIMEOUT,
        query_payload=None,
    ):
        """Initialize the data object."""
        self._http_session = http_session
        self._timeout = timeout
        self._flume_auth = flume_auth
        self._scan_interval = scan_interval
        self.device_id = device_id
        self.values = {}
        if query_payload is None:
            self._query_payload = _generate_api_query_payload(self._scan_interval)
        self._query_keys = [q["request_id"] for q in self._query_payload["queries"]]
        if update_on_init:
            self.update()

    @sleep_and_retry
    @limits(calls=2, period=API_LIMIT)
    def update(self):
        """Return updated value for session."""
        return self.update_force()

    def update_force(self):
        """Return updated value for session without auto retry or limits."""
        self._flume_auth.read_token_file()

        url = API_QUERY_URL.format(
            user_id=self._flume_auth.user_id, device_id=self.device_id
        )
        response = self._http_session.post(
            url,
            json=self._query_payload,
            headers=self._flume_auth.authorization_header,
            timeout=self._timeout,
        )

        LOGGER.debug("Update URL: %s", url)
        LOGGER.debug("Update query_payload: %s", self._query_payload)
        LOGGER.debug("Update Response: %s", response.text)

        # Check for response errors.
        _response_error(
            f"Can't update flume data for user id {self._flume_auth.user_id}", response
        )

        responses = response.json()["data"][0]

        self.values = {
            k: responses[k][0]["value"] if len(responses[k]) == 1 else None
            for k in self._query_keys
        }
