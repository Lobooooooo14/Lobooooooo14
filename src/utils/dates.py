import calendar
from datetime import datetime


def get_current_month_interval() -> tuple[str, str]:
    """
    Get the first and last day of the current month in ISO format.

    Returns
    -------
    tuple[str, str]: A tuple containing the first
    and last day of the current month in ISO format.

    Example
    --------
    >>> get_current_month_interval()
    ('2023-06-01T00:00:00Z', '2023-06-30T23:59:59Z')
    """

    now = datetime.now()

    first_day_of_current_month = datetime(now.year, now.month, 1)
    last_day_of_current_month = datetime(
        now.year, now.month, calendar.monthrange(now.year, now.month)[1]
    )

    first_iso = first_day_of_current_month.strftime("%Y-%m-%dT00:00:00Z")
    last_iso = last_day_of_current_month.strftime("%Y-%m-%dT23:59:59Z")

    return first_iso, last_iso
