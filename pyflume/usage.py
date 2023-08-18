"""Retrieve usage alert notifications from Flume API."""
from requests import Session

from .constants import API_USAGE_URL, DEFAULT_TIMEOUT  # noqa: WPS300
from .utils import configure_logger, flume_response_error  # noqa: WPS300

# Configure logging
LOGGER = configure_logger(__name__)


class FlumeUsageAlertList(object):
    """Get Flume Usage Alert list from API."""

    def __init__(
        self,
        flume_auth,
        http_session=None,
        timeout=DEFAULT_TIMEOUT,
        read="false",
    ):
        """

        Initialize the data object.

        Args:
            flume_auth: Authentication object.
            http_session: Requests Session()
            timeout: Requests timeout for throttling.
            read: state of usage alert list, have they been read, not read.

        """
        self._timeout = timeout
        self._flume_auth = flume_auth
        self._read = read

        if http_session is None:
            self._http_session = Session()
        else:
            self._http_session = http_session

        self.usage_alert_list = self.get_usage_alerts()

    def get_usage_alerts(self):
        """Return all usage alerts from devices owned by teh user.

        Returns:
            Returns JSON list of usage alerts.
        """

        url = API_USAGE_URL.format(user_id=self._flume_auth.user_id)

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

        LOGGER.debug(f"get_usage_alerts Response: {response.text}")

        # Check for response errors.
        flume_response_error("Impossible to retrieve usage alert", response)
        return response.json()["data"]
