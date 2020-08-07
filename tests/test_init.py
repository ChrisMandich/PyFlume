"""Basic tests for flume."""
from datetime import timedelta
import os
import unittest
from unittest.mock import patch

import pyflume
from pyflume import (
    API_DEVICES_URL,
    API_NOTIFICATIONS_URL,
    API_QUERY_URL,
    URL_OAUTH_TOKEN,
)
from requests import Session
import requests_mock

CONST_TOKEN_FILE = 'token.json'  # noqa: S105
CONST_HTTP_METHOD_POST = 'post'
CONST_USERNAME = 'username'  # noqa: S105
CONST_PASSWORD = 'password'  # noqa: S105
CONST_CLIENT_ID = 'client_id'  # noqa: S105
CONST_CLIENT_SECRET = 'client_secret'  # noqa: S105
CONST_USER_ID = 'user_id'
CONST_READ_TOKEN_FILE = 'pyflume.FlumeAuth._read_token_file'  # noqa: S105
CONST_WRITE_TOKEN_FILE = 'pyflume.FlumeAuth.write_token_file'  # noqa: S105


def load_fixture(filename):
    """

    Load a fixture.

    Args:
        filename: File to load fixture.

    Returns:
        File fixture contents.

    """
    path = os.path.join(os.path.dirname(__file__), 'fixtures', filename)
    with open(path) as fptr:
        return fptr.read()


SCAN_INTERVAL = timedelta(minutes=1)  # Using datetime


class TestFlumeAuth(unittest.TestCase):
    """Flume Auth Test Case."""

    @requests_mock.Mocker()
    @patch(CONST_READ_TOKEN_FILE, side_effect=FileNotFoundError)
    @patch(CONST_WRITE_TOKEN_FILE)
    def test_init(self, mock, read_token_mock, write_token_mock):
        """

        Test initialization for Flume Auth.

        Args:
            mock: Requests mock.
            read_token_mock: Requests mock token read.
            write_token_mock: Requests mock token write.

        """
        mock.register_uri(CONST_HTTP_METHOD_POST, URL_OAUTH_TOKEN, text=load_fixture(CONST_TOKEN_FILE))
        auth = pyflume.FlumeAuth(
            CONST_USERNAME, CONST_PASSWORD, CONST_CLIENT_ID, CONST_CLIENT_SECRET, http_session=Session(),
        )
        assert auth.user_id == CONST_USER_ID  # noqa: S101


class TestFlumeDeviceList(unittest.TestCase):
    """Flume Device List Test Case."""

    @requests_mock.Mocker()
    @patch(CONST_READ_TOKEN_FILE, side_effect=FileNotFoundError)
    @patch(CONST_WRITE_TOKEN_FILE)
    def test_init(self, mock, read_token_mock, write_token_mock):
        """

        Test initialization for Flume Device List.

        Args:
            mock: Requests mock.
            read_token_mock: Requests mock token read.
            write_token_mock: Requests mock token write.

        """
        mock.register_uri(CONST_HTTP_METHOD_POST, URL_OAUTH_TOKEN, text=load_fixture(CONST_TOKEN_FILE))
        mock.register_uri(
            'get',
            API_DEVICES_URL.format(user_id=CONST_USER_ID),
            text=load_fixture('devices.json'),
        )
        flume_auth = pyflume.FlumeAuth(
            CONST_USERNAME, CONST_PASSWORD, CONST_CLIENT_ID, CONST_CLIENT_SECRET,
        )

        flume_devices = pyflume.FlumeDeviceList(flume_auth)
        devices = flume_devices.get_devices()
        assert len(devices) == 1  # noqa: S101
        assert devices[0][CONST_USER_ID] == 1111  # noqa: S101,WPS432


class TestFlumeNotificationList(unittest.TestCase):
    """Test Flume Notification List Test."""

    @requests_mock.Mocker()
    @patch(CONST_READ_TOKEN_FILE, side_effect=FileNotFoundError)
    @patch(CONST_WRITE_TOKEN_FILE)
    def test_init(self, mock, read_token_mock, write_token_mock):
        """

        Test initialization for Flume Notification List.

        Args:
            mock: Requests mock.
            read_token_mock: Requests mock token read.
            write_token_mock: Requests mock token write.

        """
        mock.register_uri(CONST_HTTP_METHOD_POST, URL_OAUTH_TOKEN, text=load_fixture(CONST_TOKEN_FILE))
        mock.register_uri(
            'get',
            API_NOTIFICATIONS_URL.format(user_id=CONST_USER_ID),
            text=load_fixture('notification.json'),
        )
        flume_auth = pyflume.FlumeAuth(
            CONST_USERNAME, CONST_PASSWORD, CONST_CLIENT_ID, CONST_CLIENT_SECRET,
        )

        flume_notifications = pyflume.FlumeNotificationList(flume_auth)
        notifications = flume_notifications.get_notifications()
        assert len(notifications) == 1  # noqa: S101
        assert notifications[0][CONST_USER_ID] == 1111  # noqa: S101,WPS432


class TestFlumeData(unittest.TestCase):
    """Test Flume Data Test."""

    @requests_mock.Mocker()
    @patch(CONST_READ_TOKEN_FILE, side_effect=FileNotFoundError)
    @patch(CONST_WRITE_TOKEN_FILE)
    def test_init(self, mock, read_token_mock, write_token_mock):
        """

        Test initialization for Flume Data.

        Args:
            mock: Requests mock.
            read_token_mock: Requests mock token read.
            write_token_mock: Requests mock token write.

        """
        mock.register_uri(CONST_HTTP_METHOD_POST, URL_OAUTH_TOKEN, text=load_fixture(CONST_TOKEN_FILE))
        mock.register_uri(
            CONST_HTTP_METHOD_POST,
            API_QUERY_URL.format(user_id=CONST_USER_ID, device_id='device_id'),
            text=load_fixture('query.json'),
        )

        flume_auth = pyflume.FlumeAuth(
            CONST_USERNAME, CONST_PASSWORD, CONST_CLIENT_ID, CONST_CLIENT_SECRET,
        )

        flume = pyflume.FlumeData(
            flume_auth,
            'device_id',
            'America/Los_Angeles',
            SCAN_INTERVAL,
            http_session=Session(),
            update_on_init=False,
        )
        assert flume.values == {}  # noqa: S101,WPS520
        flume.update()

        assert flume.values == {  # noqa: S101
            'current_interval': 14.38855184,
            'today': 56.6763912,
            'week_to_date': 1406.07065872,
            'month_to_date': 56.6763912,
            'last_60_min': 14.38855184,
            'last_24_hrs': 258.9557672,
            'last_30_days': 5433.56753264,
        }
