#!/usr/bin/env python3
"""Audit the release tree for local paths, secrets, and sensitive artifacts."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import zipfile
from pathlib import Path


def run_git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed:\n"
            + result.stderr.decode("utf-8", errors="replace")
        )
    return result.stdout


def repository_root() -> Path:
    here = Path(__file__).resolve()
    result = subprocess.run(
        ["git", "-C", str(here.parent), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("release_audit.py must be run inside a Git repository.")
    return Path(result.stdout.strip()).resolve()


def make_patterns() -> dict[str, re.Pattern[bytes]]:
    # Build machine-specific path fragments without embedding those literal
    # fragments in this audit script itself.
    mac_user = b"/" + b"Users" + b"/"
    linux_home = b"/" + b"home" + b"/"
    container_data = b"/" + b"mnt" + b"/" + b"data" + b"/"
    windows_user = rb"[A-Za-z]:\\" + b"Users" + rb"\\"

    return {
        "macOS user path": re.compile(re.escape(mac_user)),
        "Linux home path": re.compile(re.escape(linux_home)),
        "container data path": re.compile(re.escape(container_data)),
        "Windows user-profile path": re.compile(windows_user, re.IGNORECASE),
        "private-key header": re.compile(
            rb"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
        ),
        "AWS access key": re.compile(rb"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
        "GitHub token": re.compile(
            rb"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|"
            rb"github_pat_[A-Za-z0-9_]{20,})\b"
        ),
        "OpenAI-style API key": re.compile(rb"\bsk-[A-Za-z0-9_-]{20,}\b"),
        "Slack token": re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
        "Google API key": re.compile(rb"\bAIza[0-9A-Za-z_-]{30,}\b"),
    }


ASSIGNMENT_PATTERN = re.compile(
    rb"""(?ix)
    \b(api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password|passwd)\b
    \s*[:=]\s*[\"']([^\"'\r\n]{8,})[\"']
    """
)

PLACEHOLDER_VALUES = {
    b"your_api_key",
    b"your_token",
    b"your_password",
    b"replace_me",
    b"changeme",
    b"example",
    b"placeholder",
    b"not_set",
}

SENSITIVE_NAME_PATTERN = re.compile(
    r"""(?ix)
    (^|/)(
        support2_raw\.csv
        | support2_phase4a_audit_[^/]*\.zip
        | support2_phase4b_frozen_[^/]*\.zip
        | support2_phase4d_[^/]*\.zip
        | untouched_test_predictions\.csv
        | test_predictions\.csv
        | split_assignments[^/]*\.(csv|parquet|feather|pkl|pickle)
        | final_refit_model\.joblib
        | final_refit_preprocessor\.joblib
    )$
    """
)

IGNORED_PLACEHOLDER_SNIPPETS = (b"example", b"placeholder")
MAX_ARCHIVE_MEMBER_BYTES = 50_000_000


def printable_context(data: bytes, start: int, end: int) -> str:
    left = max(0, start - 70)
    right = min(len(data), end + 120)
    return (
        data[left:right]
        .decode("utf-8", errors="replace")
        .replace("\r", " ")
        .replace("\n", " ")
    )


def scan_bytes(
    data: bytes,
    location: str,
    patterns: dict[str, re.Pattern[bytes]],
    errors: list[str],
) -> None:
    for label, pattern in patterns.items():
        match = pattern.search(data)
        if match:
            errors.append(
                f"{label} detected in {location}:\n"
                f"  {printable_context(data, match.start(), match.end())}"
            )

    for match in ASSIGNMENT_PATTERN.finditer(data):
        value = match.group(2).strip().lower()
        if (
            value in PLACEHOLDER_VALUES
            or any(fragment in value for fragment in IGNORED_PLACEHOLDER_SNIPPETS)
            or value.startswith(b"${")
            or value.startswith(b"<")
        ):
            continue
        errors.append(
            f"Possible hard-coded credential assignment in {location}:\n"
            f"  {match.group(0).decode('utf-8', errors='replace')}"
        )


def should_scan_as_text(data: bytes) -> bool:
    return b"\x00" not in data[:8192]


def scan_archive(
    path: Path,
    relative_name: str,
    patterns: dict[str, re.Pattern[bytes]],
    errors: list[str],
) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                member = info.filename
                member_parts = Path(member).parts

                if member.startswith(("/", "\\")) or ".." in member_parts:
                    errors.append(
                        f"Unsafe archive member path in {relative_name}: {member}"
                    )

                if SENSITIVE_NAME_PATTERN.search(member):
                    errors.append(
                        "Possible participant-, split-, test-, or fitted-model "
                        f"artifact in {relative_name}: {member}"
                    )

                if info.is_dir() or info.file_size > MAX_ARCHIVE_MEMBER_BYTES:
                    continue

                member_data = archive.read(info)
                if should_scan_as_text(member_data):
                    scan_bytes(
                        member_data,
                        f"{relative_name}::{member}",
                        patterns,
                        errors,
                    )
    except zipfile.BadZipFile:
        errors.append(f"Invalid ZIP-compatible archive: {relative_name}")


def audit_current_tree(repo: Path) -> tuple[list[str], list[tuple[int, str]]]:
    patterns = make_patterns()
    errors: list[str] = []

    tracked_names = [
        name
        for name in run_git(repo, "ls-files", "-z").decode(
            "utf-8", errors="surrogateescape"
        ).split("\0")
        if name
    ]

    largest: list[tuple[int, str]] = []

    for relative_name in tracked_names:
        path = repo / relative_name

        if path.name == ".DS_Store":
            errors.append(f"Operating-system metadata is tracked: {relative_name}")
        if "__pycache__" in path.parts:
            errors.append(f"Python cache directory is tracked: {relative_name}")
        if path.suffix.lower() in {".pyc", ".pyo"}:
            errors.append(f"Python bytecode is tracked: {relative_name}")
        if path.name == ".env":
            errors.append(f"Environment file is tracked: {relative_name}")
        if path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}:
            errors.append(f"Potential credential file is tracked: {relative_name}")

        if SENSITIVE_NAME_PATTERN.search(relative_name):
            errors.append(
                "Possible participant-, split-, test-, or fitted-model artifact "
                f"is tracked: {relative_name}"
            )

        if not path.is_file():
            continue

        data = path.read_bytes()
        largest.append((len(data), relative_name))

        if should_scan_as_text(data):
            scan_bytes(data, relative_name, patterns, errors)

        if zipfile.is_zipfile(path):
            scan_archive(path, relative_name, patterns, errors)

    # Reproducibility metadata checks.
    requirements = repo / "requirements.txt"
    if requirements.is_file():
        lines = [
            line.strip()
            for line in requirements.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        unpinned = [line for line in lines if "==" not in line]
        if unpinned:
            errors.append(
                "Unpinned release requirements detected:\n  "
                + "\n  ".join(unpinned)
            )

    citation = repo / "CITATION.cff"
    if not citation.is_file():
        errors.append("CITATION.cff is missing from the repository root.")
    else:
        citation_text = citation.read_text(encoding="utf-8")
        required_fragments = (
            "cff-version: 1.2.0",
            'version: "1.0.0"',
            "repository-code:",
            "orcid:",
        )
        for fragment in required_fragments:
            if fragment not in citation_text:
                errors.append(f"CITATION.cff is missing: {fragment}")

    return errors, sorted(largest, reverse=True)


def audit_history(repo: Path) -> list[str]:
    patterns = make_patterns()
    errors: list[str] = []
    history = run_git(
        repo,
        "log",
        "--all",
        "-p",
        "--no-color",
        "--format=",
        "--no-ext-diff",
    )
    scan_bytes(history, "reachable Git history", patterns, errors)
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--current-tree-only",
        action="store_true",
        help="Audit tracked files and archive members only (default).",
    )
    mode.add_argument(
        "--include-history",
        action="store_true",
        help="Audit tracked files, archive members, and reachable Git history.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional path for a UTF-8 text report.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = repository_root()

    current_errors, largest = audit_current_tree(repo)
    history_errors = audit_history(repo) if args.include_history else []
    errors = current_errors + history_errors

    lines = [
        "PIPELINE-AWARE INFERENCE RELEASE AUDIT",
        "=" * 42,
        f"Repository: {repo}",
        f"Commit: {run_git(repo, 'rev-parse', '--short', 'HEAD').decode().strip()}",
        f"Tracked files: {len(run_git(repo, 'ls-files').splitlines())}",
        "",
        "Largest tracked files:",
    ]
    for size, name in largest[:15]:
        lines.append(f"  {size / 1024 / 1024:8.2f} MB  {name}")

    lines.append("")
    if errors:
        lines.extend(["AUDIT FAILURES", "-" * 20])
        lines.extend(f"- {error}" for error in errors)
        lines.extend(["", "PUBLIC RELEASE AUDIT: FAIL"])
    else:
        lines.extend(
            [
                "Absolute-path audit: PASS",
                "Private-key and token audit: PASS",
                "Hard-coded credential audit: PASS",
                "Participant-level artifact audit: PASS",
                "Archive member safety audit: PASS",
                "Pinned requirements audit: PASS",
                "Citation metadata audit: PASS",
                "Tracked cache/metadata audit: PASS",
            ]
        )
        if args.include_history:
            lines.append("Reachable Git-history audit: PASS")
        lines.extend(["", "PUBLIC RELEASE AUDIT: PASS"])

    report = "\n".join(lines) + "\n"
    print(report, end="")
    if args.report is not None:
        args.report.expanduser().resolve().write_text(report, encoding="utf-8")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
