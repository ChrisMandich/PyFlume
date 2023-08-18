"""Basic tests for flume. This module contains unittest classes for testing different functionalities of flume."""

# Standard library imports
from datetime import timedelta
import os
from types import MappingProxyType
import unittest

# Third-party imports
from requests import Session
import requests_mock

# Local application/library-specific imports
import pyflume

CONST_TOKEN_FILE = "token.json"  # noqa: S105
CONST_HTTP_METHOD_POST = "post"
CONST_USERNAME = "username"  # noqa: S105
CONST_PASSWORD = "password"  # noqa: S105
CONST_CLIENT_ID = "client_id"  # noqa: S105
CONST_CLIENT_SECRET = "client_secret"  # noqa: S105
CONST_USER_ID = "user_id"
CONST_FLUME_TOKEN = MappingProxyType(
    {
        "token_type": "bearer",
        "expires_in": 604800,
        "refresh_token": "fdb8fdbecf1d03ce5e6125c067733c0d51de209c",
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl9pZCIsImV4cCI6Mjk5OTk5OTk5OTcsIngiOiJ5eiJ9.utb2yzcMImBFhDx_mssC_HU0mbfo0D_-VAQOetw5_h0",
    },
)


def load_fixture(filename):
    """Load a fixture.

    Args:
        filename: File to load fixture.

    Returns:
        File fixture contents.

    """
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path) as fptr:
        return fptr.read()


SCAN_INTERVAL = timedelta(minutes=1)  # Using datetime


class TestFlumeAuth(unittest.TestCase):
    """Flume Auth Test Case."""

    @requests_mock.Mocker()
    def test_init(self, mock):
        """

        Test initialization for Flume Auth.

        Args:
            mock: Requests mock.

        """
        mock.register_uri(
            CONST_HTTP_METHOD_POST,
            pyflume.constants.URL_OAUTH_TOKEN,
            text=load_fixture(CONST_TOKEN_FILE),
        )
        auth = pyflume.FlumeAuth(
            CONST_USERNAME,
            CONST_PASSWORD,
            CONST_CLIENT_ID,
            CONST_CLIENT_SECRET,
            CONST_FLUME_TOKEN,
            http_session=Session(),
        )
        assert auth.user_id == CONST_USER_ID  # noqa: S101


class TestFlumeDeviceList(unittest.TestCase):
    """Flume Device List Test Case."""

    @requests_mock.Mocker()
    def test_init(self, mock):
        """Test initialization for Flume Device List.

        Args:
            mock: Requests mock.

        """
        mock.register_uri(
            CONST_HTTP_METHOD_POST,
            pyflume.constants.URL_OAUTH_TOKEN,
            text=load_fixture(CONST_TOKEN_FILE),
        )
        mock.register_uri(
            "get",
            pyflume.constants.API_DEVICES_URL.format(user_id=CONST_USER_ID),
            text=load_fixture("devices.json"),
        )
        flume_auth = pyflume.FlumeAuth(
            CONST_USERNAME,
            CONST_PASSWORD,
            CONST_CLIENT_ID,
            CONST_CLIENT_SECRET,
            CONST_FLUME_TOKEN,
        )

        flume_devices = pyflume.FlumeDeviceList(flume_auth)
        devices = flume_devices.get_devices()
        assert len(devices) == 1  # noqa: S101
        assert devices[0][CONST_USER_ID] == 1111  # noqa: S101,WPS432


class TestFlumeNotificationList(unittest.TestCase):
    """Test Flume Notification List Test."""

    @requests_mock.Mocker()
    def test_init(self, mock):
        """

        Test initialization for Flume Notification List.

        Args:
            mock: Requests mock.

        """
        mock.register_uri(
            CONST_HTTP_METHOD_POST,
            pyflume.constants.URL_OAUTH_TOKEN,
            text=load_fixture(CONST_TOKEN_FILE),
        )
        mock.register_uri(
            "get",
            pyflume.constants.API_NOTIFICATIONS_URL.format(user_id=CONST_USER_ID),
            text=load_fixture("notification.json"),
        )
        flume_auth = pyflume.FlumeAuth(
            CONST_USERNAME,
            CONST_PASSWORD,
            CONST_CLIENT_ID,
            CONST_CLIENT_SECRET,
            CONST_FLUME_TOKEN,
        )

        flume_notifications = pyflume.FlumeNotificationList(flume_auth)
        notifications = flume_notifications.get_notifications()
        assert len(notifications) == 1  # noqa: S101
        assert notifications[0][CONST_USER_ID] == 1111  # noqa: S101,WPS432


class TestFlumeUsageAlerts(unittest.TestCase):
    """Test Flume Usage Alerts Test."""

    @requests_mock.Mocker()
    def test_init(self, mock):
        """

        Test initialization for Flume Usage Alerts List.

        Args:
            mock: Requests mock.

        """
        mock.register_uri(
            CONST_HTTP_METHOD_POST,
            pyflume.constants.URL_OAUTH_TOKEN,
            text=load_fixture(CONST_TOKEN_FILE),
        )
        mock.register_uri(
            "get",
            pyflume.constants.API_USAGE_URL.format(user_id=CONST_USER_ID),
            text=load_fixture("usage.json"),
        )
        flume_auth = pyflume.FlumeAuth(
            CONST_USERNAME,
            CONST_PASSWORD,
            CONST_CLIENT_ID,
            CONST_CLIENT_SECRET,
            CONST_FLUME_TOKEN,
        )

        flume_alerts = pyflume.FlumeUsageAlertList(flume_auth)
        alerts = flume_alerts.get_usage_alerts()
        assert len(alerts) == 50  # noqa: S101, WPS432
        assert alerts[0]["device_id"] == "6248148189204194987"  # noqa: S101
        assert alerts[0]["event_rule_name"] == "High Flow Alert"  # noqa: S101


class TestFlumeLeakList(unittest.TestCase):
    """Test Flume Leak List Test."""

    @requests_mock.Mocker()
    def test_init(self, mock):
        """

        Test initialization for Flume Usage Leak List.

        Args:
            mock: Requests mock.

        """
        mock.register_uri(
            CONST_HTTP_METHOD_POST,
            pyflume.constants.URL_OAUTH_TOKEN,
            text=load_fixture(CONST_TOKEN_FILE),
        )
        mock.register_uri(
            "get",
            pyflume.constants.API_LEAK_URL.format(
                user_id=CONST_USER_ID, device_id="6248148189204194987"
            ),
            text=load_fixture("leak.json"),
        )
        flume_auth = pyflume.FlumeAuth(
            CONST_USERNAME,
            CONST_PASSWORD,
            CONST_CLIENT_ID,
            CONST_CLIENT_SECRET,
            CONST_FLUME_TOKEN,
        )

        flume_leaks = pyflume.FlumeLeakList(flume_auth, "6248148189204194987")
        alerts = flume_leaks.get_leak_alerts()
        assert len(alerts) == 1  # noqa: S101
        assert alerts[0]["active"]  # noqa: S101


class TestFlumeData(unittest.TestCase):
    """Test Flume Data Test."""

    @requests_mock.Mocker()
    def test_init(self, mock):
        """Test initialization for Flume Data.

        Args:
            mock: Requests mock.
        """
        mock.register_uri(
            CONST_HTTP_METHOD_POST,
            pyflume.constants.URL_OAUTH_TOKEN,
            text=load_fixture(CONST_TOKEN_FILE),
        )
        mock.register_uri(
            CONST_HTTP_METHOD_POST,
            pyflume.constants.API_QUERY_URL.format(
                user_id=CONST_USER_ID, device_id="device_id"
            ),
            text=load_fixture("query.json"),
        )

        flume_auth = pyflume.FlumeAuth(
            CONST_USERNAME,
            CONST_PASSWORD,
            CONST_CLIENT_ID,
            CONST_CLIENT_SECRET,
            CONST_FLUME_TOKEN,
        )

        flume = pyflume.FlumeData(
            flume_auth,
            "device_id",
            "America/Los_Angeles",
            SCAN_INTERVAL,
            http_session=Session(),
            update_on_init=False,
        )
        assert flume.values == {}  # noqa: S101,WPS520
        flume.update()

        assert flume.values == {  # noqa: S101
            "current_interval": 14.38855184,
            "today": 56.6763912,
            "week_to_date": 1406.07065872,
            "month_to_date": 56.6763912,
            "last_60_min": 14.38855184,
            "last_24_hrs": 258.9557672,
            "last_30_days": 5433.56753264,
        }
