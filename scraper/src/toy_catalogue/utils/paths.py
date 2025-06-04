from pathlib import Path
import hashlib


def find_project_root(filename: str = "pyproject.toml") -> Path:
    path = Path(__file__).resolve()
    for parent in path.parents:
        if (parent / filename).exists():
            return parent
    raise FileNotFoundError(f"Could not find {filename} in any parent directories")


def make_safe_folder_name(
    long_name: str, prefix_len: int = 20, hash_len: int = 8
) -> str:
    # Truncate to prefix_len characters (replace spaces etc. if you want)
    prefix = long_name[:prefix_len].rstrip().replace(" ", "_")
    # Generate short hash of full string
    h = hashlib.sha256(long_name.encode("utf-8")).hexdigest()[:hash_len]
    # Combine prefix and hash
    return f"{prefix}_{h}"
