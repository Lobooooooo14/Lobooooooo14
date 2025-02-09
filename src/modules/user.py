from dataclasses import dataclass

from src.modules.contributions_connection import ContributionsCollection
from src.utils import resolve_username


@dataclass
class User:
    name: str | None
    login: str
    avatarUrl: str
    url: str
    contributionsCollection: ContributionsCollection

    def __post_init__(self):
        if isinstance(self.contributionsCollection, dict):
            self.contributionsCollection = ContributionsCollection(
                **self.contributionsCollection
            )

    def get_total_contributions(self):
        # ruff: noqa: E501
        return self.contributionsCollection.contributionCalendar.totalContributions

    def get_username(self):
        return resolve_username(self.name, self.login)
