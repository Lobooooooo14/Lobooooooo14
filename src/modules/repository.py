from dataclasses import dataclass

from src.modules.languages import Languages


@dataclass
class Repository:
    stargazerCount: int
    description: str | None
    nameWithOwner: str
    updatedAt: str
    createdAt: str
    isFork: bool
    languages: Languages

    def __post_init__(self):
        if isinstance(self.languages, dict):
            self.languages = Languages(**self.languages)
