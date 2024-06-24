"""Basic tests for flume notifications. This module contains unittest classes for testing different functionalities of flume."""

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


class TestFlumeNotificationList(unittest.TestCase):
    """Test Flume Notification List Test."""

    @requests_mock.Mocker()
    def test_notification(self, mock):
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
        assert flume_notifications.has_next  # noqa: S101

        mock.register_uri(
            "get",
            flume_notifications.next_page,
            text=load_fixture("notification_next.json"),
        )

        notifications_next = flume_notifications.get_next_notifications()
        assert len(notifications_next) == 1  # noqa: S101
        assert notifications_next[0][CONST_USER_ID] == 1111  # noqa: S101,WPS432
        assert flume_notifications.has_next is False  # noqa: S101

        mock.register_uri(
            "get",
            pyflume.constants.API_NOTIFICATIONS_URL.format(user_id=CONST_USER_ID),
            text=load_fixture("notification_nopage.json"),
        )

        notifications_nopage = flume_notifications.get_notifications()
        assert len(notifications_nopage) == 1  # noqa: S101
        assert notifications_nopage[0][CONST_USER_ID] == 1111  # noqa: S101,WPS432
        assert flume_notifications.has_next is False  # noqa: S101
