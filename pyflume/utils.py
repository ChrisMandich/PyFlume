"""All functions to support Flume App."""
from datetime import datetime, timedelta
import json
import logging


def configure_logger(name):
    """Configure and return a custom logger for the given name.

    Args:
        name (string): Name of logger

    Returns:
        object: Logger Handler
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    logger_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "{asctime} - {name} - {levelname} - {message}",
        style="{",
    )
    logger_handler.setFormatter(formatter)

    logger.addHandler(logger_handler)

    return logger


def format_time(time):
    """
    Format time based on strftime.

    Args:
        time: Expected time as datetime.datetime class

    Returns:
        Formatted time.

    """
    return time.replace(second=0).strftime("%Y-%m-%d %H:%M:%S")  # noqa: WPS323


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


class FlumeResponseError(Exception):
    """
    Exception raised for errors in the Flume response.

    Attributes:
        message -- explanation of the error
    """


def flume_response_error(message, response):
    """Define a function to handle response errors from the Flume API.

    Args:
        message (string): Message received as error
        response (string): Response received as error

    Raises:
        FlumeResponseError: Exception raised when the status code is not 200.
    """
    # If the response code is 200 (OK), no error has occurred, so return immediately
    if response.status_code == 200:  # noqa: WPS432
        return

    # If the response code is 400 (Bad Request), retrieve the detailed error message
    if response.status_code == 400:  # noqa: WPS432
        error_message = json.loads(response.text)["detailed"][0]
    else:
        # For other error codes, retrieve the general error message
        error_message = json.loads(response.text)["message"]

    # Raise a custom exception with a formatted message containing the error details
    raise FlumeResponseError(
        "Message:{0}.\nResponse code returned:{1}.\nError message returned:{2}.".format(
            message, response.status_code, error_message,
        ),
    )
