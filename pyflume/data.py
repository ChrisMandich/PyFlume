"""Retrieve data from Flume API."""
from datetime import datetime, timedelta, timezone

from ratelimit import limits, sleep_and_retry
from requests import Session

from .constants import (  # noqa: WPS300
    API_LIMIT,
    API_QUERY_URL,
    CONST_OPERATION,
    CONST_UNIT_OF_MEASUREMENT,
    DEFAULT_TIMEOUT,
)
from .utils import (  # noqa: WPS300
    configure_logger,
    flume_response_error,
    format_start_month,
    format_start_today,
    format_start_week,
    format_time,
)

try:
    from zoneinfo import ZoneInfo  # noqa: WPS433
except ImportError:  # Python < 3.9
    from backports.zoneinfo import ZoneInfo  # noqa: WPS433,WPS440

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
            self.query_payload = self._generate_api_query_payload(
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
        self.query_payload = self._generate_api_query_payload(
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

    def _generate_api_query_payload(self, scan_interval, device_tz):
        """Generate API Query payload to support getting data from Flume API.

        Args:
            scan_interval (_type_): Interval to scan.
            device_tz (_type_): Time Zone of Flume device.

        Returns:
            JSON: API Query to retrieve API details.
        """
        datetime_localtime = datetime.now(timezone.utc).astimezone(ZoneInfo(device_tz))

        queries = [
            {
                "request_id": "current_interval",
                "bucket": "MIN",
                "since_datetime": format_time(
                    (datetime_localtime - scan_interval).replace(second=0),
                ),
                "until_datetime": format_time(datetime_localtime.replace(second=0)),
                "operation": CONST_OPERATION,
                "units": CONST_UNIT_OF_MEASUREMENT,
            },
            {
                "request_id": "today",
                "bucket": "DAY",
                "since_datetime": format_start_today(datetime_localtime),
                "until_datetime": format_time(datetime_localtime),
                "operation": CONST_OPERATION,
                "units": CONST_UNIT_OF_MEASUREMENT,
            },
            {
                "request_id": "week_to_date",
                "bucket": "DAY",
                "since_datetime": format_start_week(datetime_localtime),
                "until_datetime": format_time(datetime_localtime),
                "operation": CONST_OPERATION,
                "units": CONST_UNIT_OF_MEASUREMENT,
            },
            {
                "request_id": "month_to_date",
                "bucket": "MON",
                "since_datetime": format_start_month(datetime_localtime),
                "until_datetime": format_time(datetime_localtime),
                "units": CONST_UNIT_OF_MEASUREMENT,
            },
            {
                "request_id": "last_60_min",
                "bucket": "MIN",
                "since_datetime": format_time(
                    datetime_localtime - timedelta(minutes=60),
                ),
                "until_datetime": format_time(datetime_localtime),
                "operation": CONST_OPERATION,
                "units": CONST_UNIT_OF_MEASUREMENT,
            },
            {
                "request_id": "last_24_hrs",
                "bucket": "HR",
                "since_datetime": format_time(datetime_localtime - timedelta(hours=24)),
                "until_datetime": format_time(datetime_localtime),
                "operation": CONST_OPERATION,
                "units": CONST_UNIT_OF_MEASUREMENT,
            },
            {
                "request_id": "last_30_days",
                "bucket": "DAY",
                "since_datetime": format_time(
                    datetime_localtime - timedelta(days=30),  # noqa: WPS432
                ),
                "until_datetime": format_time(datetime_localtime),
                "operation": CONST_OPERATION,
                "units": CONST_UNIT_OF_MEASUREMENT,
            },
        ]
        return {"queries": queries}
