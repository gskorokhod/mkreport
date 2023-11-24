from pathlib import Path


def trim_path(path: Path, depth: int = 1) -> str:
    parts = path.parts[-depth:]
    return '/'.join(parts)
