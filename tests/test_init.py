"""Basic tests for flume."""
from datetime import timedelta
import os
import unittest
from unittest.mock import patch

import pyflume
from pyflume import API_NOTIFICATIONS_URL, API_DEVICES_URL, API_QUERY_URL, URL_OAUTH_TOKEN
from requests import Session
import requests_mock


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path) as fptr:
        return fptr.read()


SCAN_INTERVAL = timedelta(minutes=1)  # Using datetime


class TestFlumeAuth(unittest.TestCase):
    @requests_mock.Mocker()
    @patch("pyflume.FlumeAuth._read_token_file", side_effect=FileNotFoundError)
    @patch("pyflume.FlumeAuth.write_token_file")
    def test_init(self, mock, read_token_mock, write_token_mock):
        mock.register_uri("post", URL_OAUTH_TOKEN, text=load_fixture("token.json"))
        auth = pyflume.FlumeAuth(
            "username", "password", "client_id", "client_secret", http_session=Session()
        )
        assert auth.user_id == "user_id"


class TestFlumeDeviceList(unittest.TestCase):
    @requests_mock.Mocker()
    @patch("pyflume.FlumeAuth._read_token_file", side_effect=FileNotFoundError)
    @patch("pyflume.FlumeAuth.write_token_file")
    def test_init(self, mock, read_token_mock, write_token_mock):
        mock.register_uri("post", URL_OAUTH_TOKEN, text=load_fixture("token.json"))
        mock.register_uri(
            "get",
            API_DEVICES_URL.format(user_id="user_id"),
            text=load_fixture("devices.json"),
        )
        flume_auth = pyflume.FlumeAuth(
            "username", "password", "client_id", "client_secret"
        )

        flume_devices = pyflume.FlumeDeviceList(flume_auth)
        devices = flume_devices.get_devices()
        assert len(devices) == 1
        assert devices[0]["user_id"] == 1111

class TestFlumeNotificationList(unittest.TestCase):
    @requests_mock.Mocker()
    @patch("pyflume.FlumeAuth._read_token_file", side_effect=FileNotFoundError)
    @patch("pyflume.FlumeAuth.write_token_file")
    def test_init(self, mock, read_token_mock, write_token_mock):
        mock.register_uri("post", URL_OAUTH_TOKEN, text=load_fixture("token.json"))
        mock.register_uri(
            "get",
            API_NOTIFICATIONS_URL.format(user_id="user_id"),
            text=load_fixture("notification.json"),
        )
        flume_auth = pyflume.FlumeAuth(
            "username", "password", "client_id", "client_secret"
        )

        flume_notifications = pyflume.FlumeNotificationList(flume_auth)
        notifications = flume_notifications.get_notifications()
        assert len(notifications) == 1
        assert notifications[0]["user_id"] == 1111

class TestFlumeData(unittest.TestCase):
    @requests_mock.Mocker()
    @patch("pyflume.FlumeAuth._read_token_file", side_effect=FileNotFoundError)
    @patch("pyflume.FlumeAuth.write_token_file")
    def test_init(self, mock, read_token_mock, write_token_mock):
        mock.register_uri("post", URL_OAUTH_TOKEN, text=load_fixture("token.json"))
        mock.register_uri(
            "post",
            API_QUERY_URL.format(user_id="user_id", device_id="device_id"),
            text=load_fixture("query.json"),
        )

        flume_auth = pyflume.FlumeAuth(
            "username", "password", "client_id", "client_secret"
        )

        flume = pyflume.FlumeData(
            flume_auth,
            "device_id",
            SCAN_INTERVAL,
            http_session=Session(),
            update_on_init=False,
        )
        assert flume.values == {}
        flume.update()
        print(flume.values)
        assert flume.values == {
            'current_interval': 14.38855184,
            'current_min': 0,
            'today': 56.6763912,
            'week_to_date': 1406.07065872,
            'month_to_date': 56.6763912,
            'last_60_min': 14.38855184,
            'last_24_hrs': 258.9557672,
            'last_30_days': 5433.56753264
        }
