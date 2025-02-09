def resolve_username(name: str | None, login: str) -> str:
    return (name if name else login).strip()
