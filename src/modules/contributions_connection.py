from dataclasses import dataclass

from src.modules.contributions_calendar import ContributionsCalendar


@dataclass
class ContributionsCollection:
    contributionCalendar: ContributionsCalendar

    def __post_init__(self):
        if isinstance(self.contributionCalendar, dict):
            self.contributionCalendar = ContributionsCalendar(
                **self.contributionCalendar
            )
