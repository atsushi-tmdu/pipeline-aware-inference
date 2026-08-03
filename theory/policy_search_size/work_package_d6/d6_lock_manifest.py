from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable


EXCLUDED_DIRS = {
    "__pycache__",
    "outputs",
    "preflight_output",
    "results_freeze",
    ".pytest_cache",
    ".mypy_cache",
}
MANIFEST_NAME = "D6_LOCK_MANIFEST_SHA256.txt"


def iter_lock_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if relative.name == MANIFEST_NAME:
            continue
        yield path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def render_manifest(root: Path) -> str:
    lines = [
        f"{sha256(path)}  {path.relative_to(root).as_posix()}"
        for path in iter_lock_files(root)
    ]
    if not lines:
        raise RuntimeError("D6 lock manifest would be empty")
    return "\n".join(lines) + "\n"


def write_manifest(root: Path) -> Path:
    path = root / MANIFEST_NAME
    path.write_text(render_manifest(root), encoding="utf-8")
    return path


def main() -> None:
    root = Path(__file__).resolve().parent
    path = write_manifest(root)
    print(f"Wrote {path}")
    print(f"Entries: {len(path.read_text(encoding='utf-8').splitlines())}")


if __name__ == "__main__":
    main()
