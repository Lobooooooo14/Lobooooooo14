from dataclasses import dataclass
from . import ContributionsCollection


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
