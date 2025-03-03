import logging
from pathlib import Path


def get_graphql_query(query_name: str) -> str:
    """
    Gets the content of a GraphQL query located in the "queries" directory.

    Args
    ----
    query_name : str
        The name of the query, without the extension.

    Raises
    ------
    FileNotFoundError
        If the query file is not found.

    Returns
    -------
    str
        The content of the query file
    """

    query_file = f"""{query_name}.graphql"""

    path = Path(__file__).parent.parent / "queries" / query_file

    if not path.exists() or not path.is_file():
        logging.error(f"Graphql query file in {path.absolute()} not found")
        raise FileNotFoundError(
            f"Graphql query file in {path.absolute()} not found"
        )

    with path.open("r", encoding="utf-8") as file:
        return file.read()


def get_template_path(template_name: str, ext: str) -> Path:
    """Gets the path of a template file located in the "templates" directory.

    Args
    ----
    template_name : str
        The name of the template, without the extension.
    ext : str
        The extension of the template file.

    Raises
    ------
    FileNotFoundError
        If the template file is not found.

    Returns
    -------
    Path
        The path of the template file.
    """

    template_file = f"""{template_name}.{ext}"""

    path = Path(__file__).parent.parent / "templates" / template_file

    if not path.exists() or not path.is_file():
        logging.error(f"Template file in {path.absolute()} not found")
        raise FileNotFoundError(
            f"Template file in {path.absolute()} not found"
        )

    return path


def get_blacklisted_users() -> list[str]:
    """
    Gets the list of blacklisted usernames from the "blacklist.txt" file.

    Returns
    -------
    list[str]
        The list of blacklisted usernames
    """

    blacklist = []

    path = Path(__file__).parent.parent.parent / "assets" / "blacklist.txt"

    if not path.exists() or not path.is_file():
        logging.error(f"Blacklist file in {path.absolute()} not found")
        raise FileNotFoundError(
            f"Blacklist file in {path.absolute()} not found"
        )

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                logging.warning("Skipping empty line in blacklist file")
                continue

            blacklist.append(line.strip())

    return blacklist
