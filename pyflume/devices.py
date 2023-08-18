"""Retrieve Devices from Flume API."""
from requests import Session

from .constants import API_DEVICES_URL, DEFAULT_TIMEOUT  # noqa: WPS300
from .utils import configure_logger, flume_response_error  # noqa: WPS300

# Configure logging
LOGGER = configure_logger(__name__)


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
        query_string = {"user": "true", "location": "true"}

        response = self._http_session.request(
            "GET",
            url,
            headers=self._flume_auth.authorization_header,
            params=query_string,
            timeout=self._timeout,
        )

        LOGGER.debug("get_devices Response: %s", response.text)  # noqa: WPS323

        # Check for response errors.
        flume_response_error("Impossible to retreive devices", response)

        return response.json()["data"]
