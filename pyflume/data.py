"""Retrieve data from Flume API."""
from ratelimit import limits, sleep_and_retry
from requests import Session

from .constants import API_LIMIT, API_QUERY_URL, DEFAULT_TIMEOUT  # noqa: WPS300
from .utils import (  # noqa: WPS300
    configure_logger,
    flume_response_error,
    generate_api_query_payload,
)

# Configure logging
LOGGER = configure_logger(__name__)


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
            self.query_payload = generate_api_query_payload(
                self._scan_interval,
                device_tz,
            )
        else:
            self.query_payload = query_payload
        if http_session is None:
            self._http_session = Session()
        else:
            self._http_session = http_session
        self._query_keys = [
            query["request_id"] for query in self.query_payload["queries"]
        ]
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
        self.query_payload = generate_api_query_payload(
            self._scan_interval,
            self.device_tz,
        )

        url = API_QUERY_URL.format(
            user_id=self._flume_auth.user_id,
            device_id=self.device_id,
        )
        response = self._http_session.post(
            url,
            json=self.query_payload,
            headers=self._flume_auth.authorization_header,
            timeout=self._timeout,
        )

        LOGGER.debug("Update URL: %s", url)  # noqa: WPS323
        LOGGER.debug("Update query_payload: %s", self.query_payload)  # noqa: WPS323
        LOGGER.debug("Update Response: %s", response.text)  # noqa: WPS323

        # Check for response errors.
        flume_response_error(
            "Can't update flume data for user id {0}".format(self._flume_auth.user_id),
            response,
        )

        responses = response.json()["data"][0]

        self.values = {  # noqa: WPS110
            k: responses[k][0]["value"]
            if len(responses[k]) == 1
            else None  # noqa: WPS221,WPS111
            for k in self._query_keys  # noqa: WPS111
        }
