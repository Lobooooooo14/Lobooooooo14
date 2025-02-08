from dataclasses import dataclass


@dataclass
class PageInfo:
    endCursor: str
    hasNextPage: bool
