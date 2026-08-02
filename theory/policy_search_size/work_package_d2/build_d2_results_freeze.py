from __future__ import annotations

import gzip
import hashlib
import io
import json
import shutil
import tarfile
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "outputs" / "full_v1"
FROZEN = HERE / "frozen_results" / "v1"
ARCHIVE_DIR = (
    Path.home()
    / "Documents"
    / "policy-search-size-theory-archives"
    / "d2_v1"
)
ARCHIVE = ARCHIVE_DIR / "d2_numerical_validation_v1_full_outputs.tar.gz"
ARCHIVE_SHA = ARCHIVE.with_suffix(ARCHIVE.suffix + ".sha256")
RESULTS_MANIFEST = FROZEN / "D2_RESULTS_FREEZE_MANIFEST.json"

LOCK_TAG = "tess-theory-work-package-d2-v1-lock-20260802"
LOCK_COMMIT = "1ed5cac"
RESULT_TAG = "tess-theory-work-package-d2-v1-results-final-20260802"

REQUIRED_SOURCE = [
    "D2_VALIDATION_ADJUDICATION.md",
    "D2_VALIDATION_BENCHMARKS.json",
    "D2_VALIDATION_CELL_SUMMARY.csv",
    "D2_VALIDATION_CHECKS.json",
    "D2_VALIDATION_MANIFEST.json",
    "D2_VALIDATION_REPLICATIONS.csv.gz",
    "D2_VALIDATION_SUMMARY.json",
]
TRACKED_FROM_SOURCE = [
    "D2_VALIDATION_ADJUDICATION.md",
    "D2_VALIDATION_BENCHMARKS.json",
    "D2_VALIDATION_CELL_SUMMARY.csv",
    "D2_VALIDATION_CHECKS.json",
    "D2_VALIDATION_MANIFEST.json",
    "D2_VALIDATION_SUMMARY.json",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def add_file_deterministic(
    tar: tarfile.TarFile,
    source: Path,
    arcname: str,
) -> None:
    data = source.read_bytes()
    info = tarfile.TarInfo(name=arcname)
    info.size = len(data)
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mode = 0o644
    tar.addfile(info, io.BytesIO(data))


def create_deterministic_archive(files: list[tuple[Path, str]]) -> None:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    with ARCHIVE.open("wb") as raw:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=raw,
            mtime=0,
        ) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tar:
                for source, arcname in sorted(files, key=lambda item: item[1]):
                    add_file_deterministic(tar, source, arcname)


def main() -> None:
    missing = [name for name in REQUIRED_SOURCE if not (SOURCE / name).is_file()]
    if missing:
        raise SystemExit(
            "Required D2 full-run files are missing:\n- "
            + "\n- ".join(missing)
        )

    summary = json.loads(
        (SOURCE / "D2_VALIDATION_SUMMARY.json").read_text(encoding="utf-8")
    )
    expected = {
        "status": "PASS",
        "cell_count": 36,
        "outer_repetitions_per_cell": 3000,
        "bootstrap_repetitions_per_outer": 999,
        "master_seed": 20261017,
        "failed_diagnostic_check_count": 0,
        "failed_scientific_check_count": 0,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise SystemExit(
                f"Unexpected locked result for {key}: "
                f"{summary.get(key)!r} != {value!r}"
            )

    if FROZEN.exists():
        shutil.rmtree(FROZEN)
    FROZEN.mkdir(parents=True)

    for name in TRACKED_FROM_SOURCE:
        shutil.copy2(SOURCE / name, FROZEN / name)

    adjudication = HERE / "D2_POST_RUN_ADJUDICATION.md"
    if not adjudication.is_file():
        raise SystemExit("D2_POST_RUN_ADJUDICATION.md is missing")
    shutil.copy2(adjudication, FROZEN / adjudication.name)

    full_log = HERE / "D2_FULL_RUN_LOG.txt"
    review_output = HERE / "D2_REVIEW_OUTPUT.txt"

    if full_log.is_file():
        shutil.copy2(full_log, FROZEN / full_log.name)

    archive_files: list[tuple[Path, str]] = []
    for name in REQUIRED_SOURCE:
        archive_files.append(
            (SOURCE / name, f"outputs/full_v1/{name}")
        )
    archive_files.append(
        (adjudication, "D2_POST_RUN_ADJUDICATION.md")
    )
    if full_log.is_file():
        archive_files.append((full_log, full_log.name))
    if review_output.is_file():
        archive_files.append((review_output, review_output.name))

    create_deterministic_archive(archive_files)
    archive_digest = sha256(ARCHIVE)
    ARCHIVE_SHA.write_text(
        f"{archive_digest}  {ARCHIVE.name}\n",
        encoding="utf-8",
    )

    tracked_records = []
    for path in sorted(FROZEN.iterdir()):
        if path.is_file() and path.name != RESULTS_MANIFEST.name:
            tracked_records.append(
                {
                    "file": path.relative_to(HERE).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )

    manifest = {
        "study_id": "TESS_THEORY_D2_NUMERICAL_VALIDATION_V1",
        "locked_status": "PASS",
        "scientific_interpretation": (
            "Estimated-trigger two-bank first-order theory and "
            "bootstrap-normal inference validated in every primary "
            "and main-regime cell"
        ),
        "lock_tag": LOCK_TAG,
        "lock_commit": LOCK_COMMIT,
        "recommended_results_tag": RESULT_TAG,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_directory": SOURCE.relative_to(HERE).as_posix(),
        "external_archive": {
            "path": str(ARCHIVE).replace(str(Path.home()), "~", 1),
            "size_bytes": ARCHIVE.stat().st_size,
            "sha256": archive_digest,
            "sha256_file": str(ARCHIVE_SHA).replace(str(Path.home()), "~", 1),
        },
        "tracked_files": tracked_records,
        "locked_run_summary": summary,
    }
    RESULTS_MANIFEST.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("D2 results freeze created")
    print(f"Tracked directory: {FROZEN}")
    print(f"External archive: {ARCHIVE}")
    print(f"Archive SHA-256: {archive_digest}")
    print(f"Results manifest: {RESULTS_MANIFEST}")


if __name__ == "__main__":
    main()
