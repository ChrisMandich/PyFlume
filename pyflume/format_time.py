"""All functions for formatting time."""

from datetime import datetime, timedelta


def format_time(time):
    """
    Format time based on strftime.

    Args:
        time: Expected time as datetime.datetime class

    Returns:
        Formatted time.

    """
    return time.replace(second=0).strftime('%Y-%m-%d %H:%M:%S')  # noqa: WPS323


def format_start_today(time):
    """
    Format time starting at 00:00:00 provided datetime.

    Args:
        time: Expected time as datetime.datetime class

    Returns:
        Formatted time.

    """
    return format_time(datetime.combine(time, datetime.min.time()))


def format_start_month(time):
    """
    Format time starting at the first of the month for provided datetime.

    Args:
        time: Expected time as datetime.datetime class

    Returns:
        Formatted time.

    """
    return format_time(
        datetime.combine(
            time.replace(day=1),
            datetime.min.time(),
        ),
    )


def format_start_week(time):
    """
    Format time starting at the start of week for provided datetime.

    Args:
        time: Expected time as datetime.datetime class

    Returns:
        Formatted time.

    """
    return format_time(
        datetime.combine(
            time - timedelta(days=time.weekday()),
            datetime.min.time(),
        ),
    )
