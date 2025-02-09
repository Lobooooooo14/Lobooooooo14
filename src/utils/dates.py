import calendar
from datetime import datetime


def get_current_month_interval() -> tuple[str, str]:
    now = datetime.now()

    first_day = datetime(now.year, now.month, 1)
    last_day = datetime(
        now.year, now.month, calendar.monthrange(now.year, now.month)[1]
    )

    first_iso = first_day.strftime("%Y-%m-%dT00:00:00Z")
    last_iso = last_day.strftime("%Y-%m-%dT23:59:59Z")

    return first_iso, last_iso
