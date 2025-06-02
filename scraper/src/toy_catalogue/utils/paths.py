from pathlib import Path


def find_project_root(filename="pyproject.toml") -> Path:
    path = Path(__file__).resolve()
    for parent in path.parents:
        if (parent / filename).exists():
            return parent
    raise FileNotFoundError(f"Could not find {filename} in any parent directories")
