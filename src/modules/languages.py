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
