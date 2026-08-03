from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "D4_LOCK_MANIFEST.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = []
    for record in payload["files"]:
        path = ROOT / record["file"]
        if not path.is_file():
            errors.append(f"MISSING: {record['file']}")
            continue
        observed = sha256(path)
        if observed != record["sha256"]:
            errors.append(
                f"HASH MISMATCH: {record['file']}\n"
                f" expected: {record['sha256']}\n"
                f" observed: {observed}"
            )
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"D4 lock manifest verification PASS: {len(payload['files'])} files")


if __name__ == "__main__":
    main()
