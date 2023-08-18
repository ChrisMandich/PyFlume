"""Authenticates to Flume API."""
from requests import Session

from .constants import API_NOTIFICATIONS_URL, DEFAULT_TIMEOUT
from .utils import configure_logger, flume_response_error

# Configure logging
LOGGER = configure_logger(__name__)


class FlumeNotificationList(object):
    """Get Flume Notifications list from API."""

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

        LOGGER.debug("get_notifications Response: %s", response.text)  # noqa: WPS323

        # Check for response errors.
        flume_response_error("Impossible to retrieve notifications", response)
        return response.json()["data"]
