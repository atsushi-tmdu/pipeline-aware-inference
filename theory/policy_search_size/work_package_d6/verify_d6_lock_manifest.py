from __future__ import annotations

from pathlib import Path

from d6_lock_manifest import MANIFEST_NAME, sha256


def parse_manifest(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as exc:
            raise ValueError(
                f"invalid manifest line {line_number}: {line!r}"
            ) from exc
        if len(digest) != 64:
            raise ValueError(
                f"invalid SHA-256 on manifest line {line_number}"
            )
        rows.append((digest, relative))
    if not rows:
        raise ValueError("D6 lock manifest is empty")
    return rows


def verify_manifest(root: Path) -> dict[str, object]:
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.is_file():
        return {
            "pass": False,
            "reason": "manifest is missing",
            "checked": 0,
            "missing": [],
            "mismatched": [],
        }

    rows = parse_manifest(manifest_path)
    missing: list[str] = []
    mismatched: list[str] = []
    for expected, relative in rows:
        path = root / relative
        if not path.is_file():
            missing.append(relative)
            continue
        if sha256(path) != expected:
            mismatched.append(relative)

    return {
        "pass": not missing and not mismatched,
        "reason": "PASS" if not missing and not mismatched else "FAIL",
        "checked": len(rows),
        "missing": missing,
        "mismatched": mismatched,
    }


def main() -> None:
    root = Path(__file__).resolve().parent
    result = verify_manifest(root)
    print("=" * 72)
    print("D6 lock manifest verification")
    print("=" * 72)
    print(f"Checked: {result['checked']}")
    print(f"Missing: {len(result['missing'])}")
    print(f"Mismatched: {len(result['mismatched'])}")
    print(f"Status: {result['reason']}")
    if not result["pass"]:
        for label in ("missing", "mismatched"):
            for relative in result[label]:
                print(f"{label.upper()}: {relative}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
