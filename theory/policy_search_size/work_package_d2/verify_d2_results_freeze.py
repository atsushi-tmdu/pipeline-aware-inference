from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "frozen_results" / "v1" / "D2_RESULTS_FREEZE_MANIFEST.json"


def expand_home(path_text: str) -> Path:
    if path_text.startswith("~/"):
        return Path.home() / path_text[2:]
    return Path(path_text)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    if not MANIFEST.is_file():
        raise SystemExit(f"Missing manifest: {MANIFEST}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []

    for record in manifest["tracked_files"]:
        path = HERE / record["file"]
        if not path.is_file():
            errors.append(f"MISSING tracked file: {record['file']}")
            continue
        observed = sha256(path)
        if observed != record["sha256"]:
            errors.append(
                f"HASH MISMATCH tracked file: {record['file']}\n"
                f" expected: {record['sha256']}\n"
                f" observed: {observed}"
            )

    archive = expand_home(manifest["external_archive"]["path"])
    if not archive.is_file():
        errors.append(f"MISSING external archive: {archive}")
    else:
        observed = sha256(archive)
        expected = manifest["external_archive"]["sha256"]
        if observed != expected:
            errors.append(
                f"HASH MISMATCH external archive: {archive}\n"
                f" expected: {expected}\n"
                f" observed: {observed}"
            )

    if errors:
        print("\n".join(errors))
        raise SystemExit(1)

    print(
        "D2 results freeze verification PASS: "
        f"{len(manifest['tracked_files'])} tracked files + external archive"
    )


if __name__ == "__main__":
    main()
