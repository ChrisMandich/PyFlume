"""Retrieve notifications from Flume API."""
from typing import Any, Dict, Optional

from requests import Session

from .constants import (  # noqa: WPS300
    API_BASE_URL,
    API_NOTIFICATIONS_URL,
    DEFAULT_TIMEOUT,
)
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
        self.has_next = False
        self.next_page = None
        self.notification_list = self.get_notifications()

    def get_notifications(self) -> Dict[str, Any]:
        """Return all notifications from devices owned by the user.

        Returns:
            Dict[str, Any]: Notification JSON message from API.
        """

        api_url = API_NOTIFICATIONS_URL.format(user_id=self._flume_auth.user_id)

        query_string = {
            "limit": "50",
            "offset": "0",
            "sort_direction": "ASC",
            "read": self._read,
        }

        return self._get_notification_request(api_url, query_string)

    def get_next_notifications(self):
        """Return next page of notification from devices owned by the user.

        Returns:
            Returns JSON list of notifications.

        Raises:
            ValueError: If no next page is available.
        """
        if self.has_next:
            api_url = f"{API_BASE_URL}{self.next_page}"
            query_string = {}
        else:
            raise ValueError("No next page available.")
        return self._get_notification_request(api_url, query_string)

    def _has_next_page(self, response_json):
        """Return True if the next page exists.

        Args:
            response_json (Object): Response from API.

        Returns:
            Boolean: Returns true if next page exists, False if not.
        """
        if response_json is None or response_json.get("pagination") is None:
            return False

        return (
            "next" in response_json["pagination"]
            and response_json["pagination"]["next"] is not None
        )

    def _get_notification_request(self, api_url, query_string):
        """Make an API request to get usage alerts from the Flume API.

        Args:
            api_url (string): URL for request
            query_string (object): query string options

        Returns:
            object: Reponse in JSON format from API.
        """

        response = self._http_session.request(
            "GET",
            api_url,
            headers=self._flume_auth.authorization_header,
            params=query_string,
            timeout=self._timeout,
        )

        LOGGER.debug(f"_get_notification_request Response: {response.text}")

        # Check for response errors.
        flume_response_error("Impossible to retrieve notifications", response)

        response_json = response.json()
        if self._has_next_page(response_json):
            self.next_page = response_json["pagination"]["next"]
            self.has_next = True
            LOGGER.debug(
                f"Next page for Notification results: {self.next_page}",
            )
        else:
            self.has_next = False
            self.next_page = None
            LOGGER.debug("No further pages for Notification results.")
        return response_json["data"]
