#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

FORMATS = ("pdf", "png", "svg")

MAIN_MAP = {
    "Figure1_policy_framework": "Figure1_policy_framework",
    "Figure2A_fixed_search_TESS_curves": "Figure2_fixed_search_TESS_curves",
    "Figure3_policy_effects_with_SUPPORT2": "Figure3_policy_effects_with_SUPPORT2",
    "Figure4A_activation_and_gain_capture": "Figure4A_activation_and_gain_capture",
    "Figure4B_activation_increment_covariance": "Figure4B_activation_increment_covariance",
}

SUPPLEMENT_MAP = {
    "FigureS1_SUPPORT2_TESS_curves": "FigureS1_SUPPORT2_TESS_curves",
    "FigureS2A_high_dependency_score_deciles": "FigureS2A_high_dependency_score_deciles",
    "FigureS2B_mixed_realistic_score_deciles": "FigureS2B_mixed_realistic_score_deciles",
    "FigureS2C_SUPPORT2_score_deciles": "FigureS2C_SUPPORT2_score_deciles",
    "FigureS3A_high_dependency_adaptive_policy_TESS_curves": "FigureS3A_high_dependency_adaptive_policy_TESS_curves",
    "FigureS3B_mixed_realistic_adaptive_policy_TESS_curves": "FigureS3B_mixed_realistic_adaptive_policy_TESS_curves",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_svg(path: Path) -> None:
    """Remove trailing horizontal whitespace from generated SVG text."""
    lines = path.read_text(encoding="utf-8").splitlines()
    normalized = "\n".join(line.rstrip(" \t") for line in lines) + "\n"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(normalized)


def assert_no_svg_trailing_whitespace(paths: list[Path]) -> None:
    problems: list[str] = []
    for path in paths:
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if line.endswith((" ", "\t")):
                problems.append(f"{path}:{line_number}")
                if len(problems) >= 20:
                    break
        if len(problems) >= 20:
            break
    if problems:
        raise RuntimeError(
            "Trailing whitespace remained in final SVG files: "
            + ", ".join(problems)
        )


def git_output(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=repo, text=True
    ).strip()


def copy_group(source: Path, destination: Path, mapping: dict[str, str]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    destination.mkdir(parents=True, exist_ok=True)
    for source_stem, final_stem in mapping.items():
        for extension in FORMATS:
            src = source / f"{source_stem}.{extension}"
            if not src.exists():
                raise FileNotFoundError(f"Missing required source figure: {src}")
            dst = destination / f"{final_stem}.{extension}"
            shutil.copy2(src, dst)
            if extension == "svg":
                normalize_svg(dst)
            records.append(
                {
                    "final_relative_path": str(dst),
                    "source_relative_path": str(src),
                    "size_bytes": dst.stat().st_size,
                    "sha256": sha256(dst),
                }
            )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--source-version", default="v1_4_8")
    parser.add_argument("--final-version", default="final_v1")
    args = parser.parse_args()

    repo = args.repo_root.expanduser().resolve()
    main_source = repo / "manuscript_tess" / "figures" / args.source_version
    supp_source = repo / "manuscript_tess" / "supplementary_figures" / args.source_version
    final_root = repo / "manuscript_tess" / args.final_version
    main_final = final_root / "figures"
    supp_final = final_root / "supplementary_figures"

    legends_source = repo / "simulations" / "ess" / "TESS_FINAL_FIGURE_LEGENDS_V1.md"
    if not legends_source.exists():
        raise FileNotFoundError(f"Missing final legends: {legends_source}")
    if not main_source.exists() or not supp_source.exists():
        raise FileNotFoundError(
            f"Expected source directories not found: {main_source} and {supp_source}"
        )

    if final_root.exists():
        shutil.rmtree(final_root)
    main_final.mkdir(parents=True)
    supp_final.mkdir(parents=True)

    records = []
    records.extend(copy_group(main_source, main_final, MAIN_MAP))
    records.extend(copy_group(supp_source, supp_final, SUPPLEMENT_MAP))

    shutil.copy2(legends_source, final_root / "FIGURE_LEGENDS.md")

    readme = f"""# TESS manuscript figure set — final v1

This directory is the canonical manuscript figure set frozen from:

- `manuscript_tess/figures/{args.source_version}`
- `manuscript_tess/supplementary_figures/{args.source_version}`

Figure 2 is one two-panel figure and has been renamed from
`Figure2A_fixed_search_TESS_curves` to `Figure2_fixed_search_TESS_curves`.

Canonical formats: PDF, PNG, and SVG.
The figures were generated from frozen processed data and reproducible code;
no generative-image output is included in this canonical set.
"""
    (final_root / "README.md").write_text(readme, encoding="utf-8")

    required_tags = [
        "tess-confirmatory-policy-v1-final-20260802",
        "tess-support2-validation-v1-final-20260802",
    ]
    resolved_tags = {}
    for tag in required_tags:
        try:
            resolved_tags[tag] = git_output(repo, "rev-list", "-n", "1", tag)
        except subprocess.CalledProcessError:
            resolved_tags[tag] = None

    manifest = {
        "asset_set": "TESS_MANUSCRIPT_FIGURES_FINAL_V1",
        "source_version": args.source_version,
        "final_version": args.final_version,
        "git_head_at_freeze": git_output(repo, "rev-parse", "HEAD"),
        "scientific_result_tags": resolved_tags,
        "main_figure_stems": list(MAIN_MAP.values()),
        "supplementary_figure_stems": list(SUPPLEMENT_MAP.values()),
        "file_count": len(records),
        "expected_file_count": (len(MAIN_MAP) + len(SUPPLEMENT_MAP)) * len(FORMATS),
        "files": records,
    }
    if manifest["file_count"] != manifest["expected_file_count"]:
        raise RuntimeError("Unexpected final figure file count")

    (final_root / "FIGURE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    final_svgs = sorted(final_root.rglob("*.svg"))
    assert_no_svg_trailing_whitespace(final_svgs)

    if any(main_final.glob("Figure2A*")):
        raise RuntimeError("Figure2A filename remains in the canonical set")
    for extension in FORMATS:
        expected = main_final / f"Figure2_fixed_search_TESS_curves.{extension}"
        if not expected.exists():
            raise RuntimeError(f"Renamed Figure 2 file missing: {expected}")

    print("TESS final manuscript figure set frozen")
    print(f"Final root: {final_root}")
    print(f"Main figure files: {len(MAIN_MAP) * len(FORMATS)}")
    print(f"Supplementary figure files: {len(SUPPLEMENT_MAP) * len(FORMATS)}")
    print(f"Total canonical figure files: {len(records)}")
    print(f"Manifest: {final_root / 'FIGURE_MANIFEST.json'}")


if __name__ == "__main__":
    main()
