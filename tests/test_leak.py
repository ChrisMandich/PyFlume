"""Basic tests for flume leaks. This module contains unittest classes for testing different functionalities of flume."""
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


class TestFlumeLeakList(unittest.TestCase):
    """Test Flume Leak List Test."""

    @requests_mock.Mocker()
    def test_leak(self, mock):
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
                user_id=CONST_USER_ID,
                device_id="6248148189204194987",
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
        alerts = flume_leaks.get_leaks()
        assert len(alerts) == 1  # noqa: S101
        assert alerts[0]["active"]  # noqa: S101
