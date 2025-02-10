from dataclasses import dataclass

from src.utils import resolve_username


@dataclass
class Viewer:
    name: str | None
    login: str
    avatarUrl: str
    url: str
    bio: str | None
    location: str | None

    def get_username(self):
        return resolve_username(self.name, self.login)
