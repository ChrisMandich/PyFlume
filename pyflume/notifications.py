"""Retrieve notifications from Flume API."""
from typing import Any, Dict, Optional

from requests import Session

from .constants import API_NOTIFICATIONS_URL, DEFAULT_TIMEOUT  # noqa: WPS300
from .utils import configure_logger, flume_response_error  # noqa: WPS300

# Configure logging
LOGGER = configure_logger(__name__)


class FlumeNotificationList(object):
    """Get Flume Notifications list from API."""

    def __init__(
        self,
        flume_auth,
        http_session: Optional[Session] = None,
        timeout: int = DEFAULT_TIMEOUT,
        read: str = "false",
    ) -> None:
        """
        Initialize the FlumeNotificationList object.

        Args:
            flume_auth: Authentication object.
            http_session: Optional Requests Session().
            timeout: Requests timeout for throttling, default DEFAULT_TIMEOUT.
            read: state of notification list, default "false".
        """
        self._timeout = timeout
        self._flume_auth = flume_auth
        self._read = read
        self._http_session = http_session or Session()
        self.notification_list = self.get_notifications()

    def get_notifications(self) -> Dict[str, Any]:
        """Return all notifications from devices owned by the user.

        Returns:
            Dict[str, Any]: Notification JSON message from API.
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

        LOGGER.debug(f"get_notifications Response: {response.text}")

        # Check for response errors.
        flume_response_error("Impossible to retrieve notifications", response)
        return response.json()["data"]
