from dataclasses import dataclass
from . import ContributionsCalendar


@dataclass
class ContributionsCollection:
    contributionCalendar: ContributionsCalendar

    def __post_init__(self):
        if isinstance(self.contributionCalendar, dict):
            self.contributionCalendar = ContributionsCalendar(
                **self.contributionCalendar
            )
