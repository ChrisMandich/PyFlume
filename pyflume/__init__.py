"""Package to interact with Flume Sensor."""

from datetime import datetime, timedelta
import json
import logging
from os import path
from tempfile import gettempdir

import jwt  # pip install pyjwt
from pyflume.format_time import (
    format_start_month,
    format_start_today,
    format_start_week,
    format_time,
)
from pytz import timezone, utc
from ratelimit import limits, sleep_and_retry
from requests import Session

TOKEN_FILE = path.join(gettempdir(), 'FLUME_TOKEN_FILE')
API_LIMIT = 60

CONST_OPERATION = 'SUM'
CONST_UNIT_OF_MEASUREMENT = 'GALLONS'

DEFAULT_TIMEOUT = 30

API_BASE_URL = 'https://api.flumetech.com'
URL_OAUTH_TOKEN = '{0}{1}'.format(API_BASE_URL, '/oauth/token')  # noqa: S105
API_QUERY_URL = '{0}{1}'.format(API_BASE_URL, '/users/{user_id}/devices/{device_id}/query')
API_DEVICES_URL = '{0}{1}'.format(API_BASE_URL, '/users/{user_id}/devices')
API_NOTIFICATIONS_URL = '{0}{1}'.format(API_BASE_URL, '/users/{user_id}/notifications')

LOGGER = logging.getLogger(__name__)


def _generate_api_query_payload(scan_interval, device_tz):
    datetime_localtime = utc.localize(datetime.utcnow()).astimezone(timezone(device_tz))

    queries = [
        {
            'request_id': 'current_interval',
            'bucket': 'MIN',
            'since_datetime': format_time(
                (datetime_localtime - scan_interval).replace(second=0),
            ),
            'until_datetime': format_time(datetime_localtime.replace(second=0)),
            'operation': CONST_OPERATION,
            'units': CONST_UNIT_OF_MEASUREMENT,
        },
        {
            'request_id': 'today',
            'bucket': 'DAY',
            'since_datetime': format_start_today(datetime_localtime),
            'until_datetime': format_time(datetime_localtime),
            'operation': CONST_OPERATION,
            'units': CONST_UNIT_OF_MEASUREMENT,
        },
        {
            'request_id': 'week_to_date',
            'bucket': 'DAY',
            'since_datetime': format_start_week(datetime_localtime),
            'until_datetime': format_time(datetime_localtime),
            'operation': CONST_OPERATION,
            'units': CONST_UNIT_OF_MEASUREMENT,
        },
        {
            'request_id': 'month_to_date',
            'bucket': 'MON',
            'since_datetime': format_start_month(datetime_localtime),
            'until_datetime': format_time(datetime_localtime),
            'units': CONST_UNIT_OF_MEASUREMENT,
        },
        {
            'request_id': 'last_60_min',
            'bucket': 'MIN',
            'since_datetime': format_time(datetime_localtime - timedelta(minutes=60)),
            'until_datetime': format_time(datetime_localtime),
            'operation': CONST_OPERATION,
            'units': CONST_UNIT_OF_MEASUREMENT,
        },
        {
            'request_id': 'last_24_hrs',
            'bucket': 'HR',
            'since_datetime': format_time(datetime_localtime - timedelta(hours=24)),
            'until_datetime': format_time(datetime_localtime),
            'operation': CONST_OPERATION,
            'units': CONST_UNIT_OF_MEASUREMENT,
        },
        {
            'request_id': 'last_30_days',
            'bucket': 'DAY',
            'since_datetime': format_time(datetime_localtime - timedelta(days=30)),  # noqa: WPS432
            'until_datetime': format_time(datetime_localtime),
            'operation': CONST_OPERATION,
            'units': CONST_UNIT_OF_MEASUREMENT,
        },
    ]
    return {'queries': queries}


def _response_error(message, response):
    if response.status_code == 200:  # noqa: WPS432
        return

    if response.status_code == 400:  # noqa: WPS432
        error_message = json.loads(response.text)['detailed'][0]
    else:
        error_message = json.loads(response.text)['message']

    raise Exception(
        """Message:{0}.
            Response code returned:{1}.
            Eror message returned:{2}.""".format(message, response.status_code, error_message),
    )


class FlumeAuth(object):  # noqa: WPS214
    """Interact with API Authentication."""

    def __init__(  # noqa: WPS211
        self,
        username,
        password,
        client_id,
        client_secret,
        flume_token_file=TOKEN_FILE,
        http_session=None,
        timeout=DEFAULT_TIMEOUT,
    ):
        """

        Initialize the data object.

        Args:
            username: Username to authenticate.
            password: Password to authenticate.
            client_id: API client id.
            client_secret: API client secret.
            flume_token_file: Token file location.
            http_session: Requests Session()
            timeout: Requests timeout for throttling.

        """

        self._creds = {
            'client_id': client_id,
            'client_secret': client_secret,
            'username': username,
            'password': password,
        }

        if http_session is None:
            self._http_session = Session()
        else:
            self._http_session = http_session

        self._timeout = timeout
        self._token_file = flume_token_file
        self._token = None
        self._decoded_token = None
        self.user_id = None
        self.authorization_header = None
        self.read_token_file()

    def fetch_token(self):
        """Return authorization token for session."""

        payload = dict({'grant_type': 'password'}, **self._creds)
        self.load_token(self.token_request(payload))
        self.write_token_file()

    def load_token(self, token):
        """
        Update _token, decode token, user_id and auth header.

        Args:
            token: Authentication bearer token to be decoded.

        """

        self._token = token
        try:
            self._decoded_token = jwt.decode(self._token['access_token'], verify=False)
        except jwt.exceptions.DecodeError:
            LOGGER.debug('Poorly formatted Access Token, fetching token using _creds')
            self.fetch_token()

        self.user_id = self._decoded_token['user_id']

        self.authorization_header = {
            'authorization': 'Bearer {0}'.format(self._token.get('access_token')),
        }

    def token_request(self, payload):
        """

        Request Authorization Payload.

        Args:
            payload: Request payload to get token request.

        Returns:
            Return response Authentication Bearer token from request.

        """

        headers = {'content-type': 'application/json'}
        response = self._http_session.request(
            'POST',
            URL_OAUTH_TOKEN,
            json=payload,
            headers=headers,
            timeout=self._timeout,
        )

        LOGGER.debug('Token Payload: %s', payload)  # noqa: WPS323
        LOGGER.debug('Token Response: %s', response.text)  # noqa: WPS323

        # Check for response errors.
        _response_error("Can't get token for user {0}".format(self._creds.get('username')), response)

        return json.loads(response.text)['data'][0]

    def read_token_file(self):
        """Read local token file and load it."""
        try:  # noqa: WPS229
            if not self._decoded_token:
                # Only re-read from disk if we do not already
                # have the token in memory
                self._read_token_file()
            self.verify_token()
        except FileNotFoundError:
            LOGGER.debug('Token file does not exist, fetching token using _creds')
            self.fetch_token()
            self.write_token_file()
        except json.decoder.JSONDecodeError:
            LOGGER.debug('Invalid JSON in token file, fetching token using _creds')
            self.fetch_token()
            self.write_token_file()

    def refresh_token(self):
        """Return authorization token for session."""

        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self._token['refresh_token'],
            'client_id': self._creds['client_id'],
            'client_secret': self._creds['client_secret'],
        }

        self.load_token(self.token_request(payload))
        self.write_token_file()

    def verify_token(self):
        """Check to see if token is expiring in 12 hours."""
        token_expiration = datetime.fromtimestamp(self._decoded_token['exp'])
        time_difference = datetime.now() + timedelta(hours=12)  # noqa: WPS432
        LOGGER.debug('Token expiration time: %s', token_expiration)  # noqa: WPS323
        LOGGER.debug('Token comparison time: %s', time_difference)  # noqa: WPS323

        if token_expiration <= time_difference:
            self.refresh_token()

    def write_token_file(self):
        """Write token locally."""
        with open(self._token_file, 'w') as token_file:
            token_file.write(json.dumps(self._token))

    def _read_token_file(self):
        """Read local token file and load it."""
        with open(self._token_file, 'r') as token_file:
            self.load_token(json.load(token_file))


class FlumeDeviceList(object):
    """Get Flume Device List from API."""

    def __init__(
        self,
        flume_auth,
        http_session=None,
        timeout=DEFAULT_TIMEOUT,
    ):
        """

        Initialize the data object.

        Args:
            flume_auth: Authentication object.
            http_session: Requests Session()
            timeout: Requests timeout for throttling.

        """
        self._timeout = timeout
        self._flume_auth = flume_auth

        if http_session is None:
            self._http_session = Session()
        else:
            self._http_session = http_session

        self.device_list = self.get_devices()

    def get_devices(self):
        """
        Return all available devices from Flume API.

        Returns:
            Json device list.

        """

        url = API_DEVICES_URL.format(user_id=self._flume_auth.user_id)
        query_string = {'user': 'true', 'location': 'true'}

        response = self._http_session.request(
            'GET',
            url,
            headers=self._flume_auth.authorization_header,
            params=query_string,
            timeout=self._timeout,
        )

        LOGGER.debug('get_devices Response: %s', response.text)  # noqa: WPS323

        # Check for response errors.
        _response_error('Impossible to retreive devices', response)

        return response.json()['data']


class FlumeNotificationList(object):
    """Get Flume Notifications list from API."""

    def __init__(
        self,
        flume_auth,
        http_session=None,
        timeout=DEFAULT_TIMEOUT,
        read='false',
    ):
        """

        Initialize the data object.

        Args:
            flume_auth: Authentication object.
            http_session: Requests Session()
            timeout: Requests timeout for throttling.
            read: state of notification list, have they been read, not read.

        """
        self._timeout = timeout
        self._flume_auth = flume_auth
        self._read = read

        if http_session is None:
            self._http_session = Session()
        else:
            self._http_session = http_session

        self.notification_list = self.get_notifications()

    def get_notifications(self):
        """
        Return all notifications from devices owned by the user.

        Returns:
            Returns JSON list of notifications.

        """

        url = API_NOTIFICATIONS_URL.format(user_id=self._flume_auth.user_id)

        query_string = {
            'limit': '50',
            'offset': '0',
            'sort_direction': 'ASC',
            'read': self._read,
        }

        response = self._http_session.request(
            'GET',
            url,
            headers=self._flume_auth.authorization_header,
            params=query_string,
            timeout=self._timeout,
        )

        LOGGER.debug('get_notifications Response: %s', response.text)  # noqa: WPS323

        # Check for response errors.
        _response_error('Impossible to retrieve notifications', response)
        return response.json()['data']


class FlumeData(object):
    """Get the latest data and update the states."""

    def __init__(  # noqa: WPS211
        self,
        flume_auth,
        device_id,
        device_tz,
        scan_interval,
        update_on_init=True,
        http_session=None,
        timeout=DEFAULT_TIMEOUT,
        query_payload=None,
    ):
        """

        Initialize the data object.

        Args:
            flume_auth: Authentication object.
            device_id: flume device id.
            device_tz: timezone of device
            scan_interval: duration of scan, ex: 60 minutes.
            update_on_init: update on initialization.
            http_session: Requests Session()
            timeout: Requests timeout for throttling.
            query_payload: Specific query_payload to request for device.

        """
        self._timeout = timeout
        self._flume_auth = flume_auth
        self._scan_interval = scan_interval
        self.device_id = device_id
        self.device_tz = device_tz
        self.values = {}  # noqa: WPS110
        if query_payload is None:
            self.query_payload = _generate_api_query_payload(
                self._scan_interval, device_tz,
            )
        if http_session is None:
            self._http_session = Session()
        else:
            self._http_session = http_session
        self._query_keys = [query['request_id'] for query in self.query_payload['queries']]
        if update_on_init:
            self.update()

    @sleep_and_retry
    @limits(calls=2, period=API_LIMIT)
    def update(self):
        """
        Return updated value for session.

        Returns:
            Returns status of update

        """
        return self.update_force()

    def update_force(self):
        """Return updated value for session without auto retry or limits."""
        self._flume_auth.read_token_file()
        self.query_payload = _generate_api_query_payload(
            self._scan_interval, self.device_tz,
        )

        url = API_QUERY_URL.format(
            user_id=self._flume_auth.user_id, device_id=self.device_id,
        )
        response = self._http_session.post(
            url,
            json=self.query_payload,
            headers=self._flume_auth.authorization_header,
            timeout=self._timeout,
        )

        LOGGER.debug('Update URL: %s', url)  # noqa: WPS323
        LOGGER.debug('Update query_payload: %s', self.query_payload)  # noqa: WPS323
        LOGGER.debug('Update Response: %s', response.text)  # noqa: WPS323

        # Check for response errors.
        _response_error(
            "Can't update flume data for user id {0}".format(self._flume_auth.user_id), response,
        )

        responses = response.json()['data'][0]

        self.values = {  # noqa: WPS110
            k: responses[k][0]['value'] if len(responses[k]) == 1 else None  # noqa: WPS221,WPS111
            for k in self._query_keys  # noqa: WPS111
        }
