"""Authenticates to Flume API."""
from datetime import datetime, timedelta
import json

import jwt  # install pyjwt
from requests import Session

from .constants import DEFAULT_TIMEOUT, URL_OAUTH_TOKEN  # noqa: WPS300
from .utils import configure_logger, flume_response_error  # noqa: WPS300

# Configure logging
LOGGER = configure_logger(__name__)


class FlumeAuth(object):  # noqa: WPS214
    """Interact with API Authentication."""

    def __init__(  # noqa: WPS211
        self,
        username,
        password,
        client_id,
        client_secret,
        flume_token=None,
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
            flume_token: Pass flume token to variable.
            http_session: Requests Session()
            timeout: Requests timeout for throttling.

        """

        self._creds = {
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password,
        }

        if http_session is None:
            self._http_session = Session()
        else:
            self._http_session = http_session

        self._timeout = timeout
        self._token = None
        self._decoded_token = None
        self.user_id = None
        self.authorization_header = None

        self._load_token(flume_token)
        self._verify_token()

    @property
    def token(self):
        """
            Return authorization token for session.

        Returns:
            Returns the current JWT token.

        """
        return self._token

    def refresh_token(self):
        """Refresh authorization token for session."""

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self._token["refresh_token"],
            "client_id": self._creds["client_id"],
            "client_secret": self._creds["client_secret"],
        }

        self._load_token(self._request_token(payload))

    def retrieve_token(self):
        """Return authorization token for session."""

        payload = dict({"grant_type": "password"}, **self._creds)
        self._load_token(self._request_token(payload))

    def _load_token(self, token):
        """
        Update _token, decode token, user_id and auth header.

        Args:
            token: Authentication bearer token to be decoded.

        """
        jwt_options = {"verify_signature": False}
        self._token = token
        try:
            self._decoded_token = jwt.decode(
                self._token["access_token"],
                options=jwt_options,
            )
        except jwt.exceptions.DecodeError:
            LOGGER.debug("Poorly formatted Access Token, fetching token using _creds")
            self.retrieve_token()
        except TypeError:
            LOGGER.debug("Token TypeError, fetching token using _creds")
            self.retrieve_token()

        self.user_id = self._decoded_token["user_id"]

        self.authorization_header = {
            "authorization": "Bearer {0}".format(self._token.get("access_token")),
        }

    def _request_token(self, payload):
        """

        Request Authorization Payload.

        Args:
            payload: Request payload to get token request.

        Returns:
            Return response Authentication Bearer token from request.

        """

        headers = {"content-type": "application/json"}
        response = self._http_session.request(
            "POST",
            URL_OAUTH_TOKEN,
            json=payload,
            headers=headers,
            timeout=self._timeout,
        )

        LOGGER.debug("Token Payload: %s", payload)  # noqa: WPS323
        LOGGER.debug("Token Response: %s", response.text)  # noqa: WPS323

        # Check for response errors.
        flume_response_error(
            "Can't get token for user {0}".format(self._creds.get("username")),
            response,
        )

        return json.loads(response.text)["data"][0]

    def _verify_token(self):
        """Check to see if token is expiring in 12 hours."""
        token_expiration = datetime.fromtimestamp(self._decoded_token["exp"])
        time_difference = datetime.now() + timedelta(hours=12)  # noqa: WPS432
        LOGGER.debug("Token expiration time: %s", token_expiration)  # noqa: WPS323
        LOGGER.debug("Token comparison time: %s", time_difference)  # noqa: WPS323

        if token_expiration <= time_difference:
            self.refresh_token()
