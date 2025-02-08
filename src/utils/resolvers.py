from src.modules import User


def resolve_username(user: User) -> str:
    return (user.name if user.name else user.login).strip()
