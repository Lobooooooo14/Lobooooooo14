def resolve_github_username(name: str | None, login: str) -> str:
    """
    Resolves the GitHub username from the name and login.

    Parameters
    ----------
    name : str | None
        The name of the GitHub user.
    login : str
        The login of the GitHub user.

    Returns
    -------
    str
        The resolved GitHub username.
    """
    return (name if name else login).strip()
