from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "REPRODUCTION_MANIFEST_SHA256.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    records = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path == OUTPUT or "__pycache__" in path.parts:
            continue
        records.append(
            {
                "file": path.relative_to(ROOT).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    OUTPUT.write_text(
        json.dumps(
            {
                "root": "theory/policy_search_size",
                "files": records,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Manifest written to: {OUTPUT}")
    print(f"Files hashed: {len(records)}")


if __name__ == "__main__":
    main()
