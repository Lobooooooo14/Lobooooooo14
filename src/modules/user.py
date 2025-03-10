from dataclasses import dataclass

from src.modules.contributions import ContributionsCollection
from src.modules.repositories import RepositoriesContributedTo
from src.utils import resolve_github_username


@dataclass
class User:
    name: str | None
    login: str
    avatarUrl: str
    url: str
    bio: str
    contributionsCollection: ContributionsCollection
    repositoriesContributedTo: RepositoriesContributedTo

    def __post_init__(self):
        if isinstance(self.contributionsCollection, dict):
            self.contributionsCollection = ContributionsCollection(
                **self.contributionsCollection
            )

        if isinstance(self.repositoriesContributedTo, dict):
            self.repositoriesContributedTo = RepositoriesContributedTo(
                **self.repositoriesContributedTo
            )

    def get_total_contributions(self):
        # ruff: noqa: E501
        return self.contributionsCollection.contributionCalendar.totalContributions

    def get_username(self):
        return resolve_github_username(self.name, self.login)
