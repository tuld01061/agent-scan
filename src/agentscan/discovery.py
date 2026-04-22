from pathlib import Path

SUPPORTED_SUFFIXES = {".yaml", ".yml", ".json", ".md", ".txt"}


def discover_paths(target: Path | str) -> list[Path]:
    path = Path(target)

    if path.is_file():
        return [path] if path.suffix.lower() in SUPPORTED_SUFFIXES else []

    if not path.is_dir():
        return []

    return sorted(
        candidate
        for candidate in path.rglob("*")
        if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_SUFFIXES
    )
