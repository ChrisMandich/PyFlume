"""Basic tests for flume Data. This module contains unittest classes for testing different functionalities of flume."""
# Standard library imports
import unittest

# Third-party imports
import requests_mock

# Local application/library-specific imports
import pyflume

from .constants import (
    CONST_CLIENT_ID,
    CONST_CLIENT_SECRET,
    CONST_FLUME_TOKEN,
    CONST_HTTP_METHOD_POST,
    CONST_PASSWORD,
    CONST_TOKEN_FILE,
    CONST_USER_ID,
    CONST_USERNAME,
)
from .utils import load_fixture


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
