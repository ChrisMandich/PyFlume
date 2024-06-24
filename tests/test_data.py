"""Basic tests for flume Data. This module contains unittest classes for testing different functionalities of flume."""

# Standard library imports
import unittest

# Third-party imports
from requests import Session
import requests_mock

# Local application/library-specific imports
import pyflume

from .constants import (
    CONST_CLIENT_ID,
    CONST_CLIENT_SECRET,
    CONST_FLUME_TOKEN,
    CONST_HTTP_METHOD_POST,
    CONST_PASSWORD,
    CONST_SCAN_INTERVAL,
    CONST_TOKEN_FILE,
    CONST_USER_ID,
    CONST_USERNAME,
)
from .utils import load_fixture


class TestFlumeData(unittest.TestCase):
    """Test Flume Data Test."""

    @requests_mock.Mocker()
    def test_data(self, mock):
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
                user_id=CONST_USER_ID,
                device_id="device_id",
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
            CONST_SCAN_INTERVAL,
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
