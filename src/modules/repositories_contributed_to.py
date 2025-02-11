from dataclasses import dataclass

from src.modules.repository import Repository


@dataclass
class RepositoriesContributedTo:
    nodes: list[Repository]

    def __post_init__(self):
        if isinstance(self.nodes, list):
            self.nodes = [Repository(**x) for x in self.nodes]
