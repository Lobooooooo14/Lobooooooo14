from dataclasses import dataclass


@dataclass
class ContributionsCalendar:
    totalContributions: int


@dataclass
class ContributionsCollection:
    contributionCalendar: ContributionsCalendar

    def __post_init__(self):
        if isinstance(self.contributionCalendar, dict):
            self.contributionCalendar = ContributionsCalendar(
                **self.contributionCalendar
            )
