"""Authenticates to Flume API, returns a list of devices and allows you to pull the latest sensor results over a period of time."""
from .auth import FlumeAuth  # noqa: WPS300
from .data import FlumeData  # noqa: WPS300
from .devices import FlumeDeviceList  # noqa: WPS300
from .notifications import FlumeNotificationList  # noqa: WPS300
from .usage import FlumeUsageAlertList  # noqa: WPS300

__all__ = ['FlumeAuth', 'FlumeData', 'FlumeDeviceList', 'FlumeNotificationList', 'FlumeUsageAlertList']
