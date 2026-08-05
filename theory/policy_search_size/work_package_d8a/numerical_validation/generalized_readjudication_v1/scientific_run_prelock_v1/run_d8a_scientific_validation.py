#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "D8-A locked scientific-run entry gate"
        )
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="verify the prelocked run package",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="execute only after runner-engine lock",
    )
    arguments = parser.parse_args()

    root = Path(__file__).resolve().parent
    checker = (
        root
        / "check_d8a_scientific_run_preflight.py"
    )

    completed = subprocess.run(
        [sys.executable, str(checker)],
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(
            completed.returncode
        )

    if arguments.execute:
        engine_lock = (
            root
            / "D8A_SCIENTIFIC_RUNNER_ENGINE_LOCK.json"
        )
        if not engine_lock.is_file():
            print(
                "Scientific execution refused: "
                "runner engine is not locked."
            )
            print(
                "Scientific simulation run: NO"
            )
            raise SystemExit(2)

        print(
            "Scientific runner engine lock found, "
            "but this prelock gate does not itself "
            "start the run."
        )
        raise SystemExit(2)

    print(
        "D8-A scientific run package preflight: PASS"
    )
    print(
        "Scientific runner engine locked: NO"
    )
    print(
        "Scientific simulation run: NO"
    )


if __name__ == "__main__":
    main()
