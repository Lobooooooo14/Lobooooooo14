from dataclasses import dataclass


@dataclass
class Language:
    name: str


@dataclass
class Languages:
    nodes: list[Language]

    def __post_init__(self):
        if isinstance(self.nodes, list):
            self.nodes = [Language(**x) for x in self.nodes]


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


@dataclass
class RepositoriesContributedTo:
    nodes: list[Repository]

    def __post_init__(self):
        if isinstance(self.nodes, list):
            self.nodes = [Repository(**x) for x in self.nodes if x is not None]
