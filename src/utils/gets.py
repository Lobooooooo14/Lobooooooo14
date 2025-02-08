from pathlib import Path


def get_query(file_name: str) -> str | None:
    path = Path(__file__).parent.parent / "queries" / file_name

    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as f:
        return f.read()


def get_template_path(file_name: str) -> Path | None:
    path = Path(__file__).parent.parent / "templates" / file_name

    if not path.exists():
        return None

    return path.absolute()
