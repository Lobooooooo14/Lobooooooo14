from dataclasses import dataclass
from . import PageInfo, User


@dataclass
class Followers:
    totalCount: int
    nodes: list[User]
    pageInfo: PageInfo

    def __post_init__(self):
        if isinstance(self.pageInfo, dict):
            self.pageInfo = PageInfo(**self.pageInfo)

        if isinstance(self.nodes, list):
            self.nodes = [User(**x) for x in self.nodes]
