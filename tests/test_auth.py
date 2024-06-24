"""Basic tests for flume Auth. This module contains unittest classes for testing different functionalities of flume."""

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
    CONST_TOKEN_FILE,
    CONST_USER_ID,
    CONST_USERNAME,
)
from .utils import load_fixture


class TestFlumeAuth(unittest.TestCase):
    """Flume Auth Test Case."""

    @requests_mock.Mocker()
    def test_auth(self, mock):
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
