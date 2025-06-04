from datetime import datetime, timezone


def get_current_time():
    """
    Get the current time.

    :return: The current date time in UTC
    :rtype: datetime
    """
    return datetime.now(timezone.utc)


def get_current_timestamp():
    """
    Get the current timestamp.

    :return: The current timestamp
    :rtype: int
    """
    return int(get_current_time().timestamp())
