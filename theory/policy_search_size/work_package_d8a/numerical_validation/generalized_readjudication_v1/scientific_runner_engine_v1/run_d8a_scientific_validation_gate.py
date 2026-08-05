#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--execute",
        action="store_true",
    )
    arguments, remainder = (
        parser.parse_known_args()
    )

    engine = Path(__file__).resolve().parent
    lock_path = (
        engine
        / "D8A_SCIENTIFIC_RUNNER_ENGINE_LOCK.json"
    )
    verifier = (
        engine
        / "verify_d8a_scientific_runner_engine_lock.py"
    )
    executor = (
        engine
        / "execute_d8a_scientific_run.py"
    )

    reasons = []
    if not lock_path.is_file():
        reasons.append(
            "runner-engine lock is absent"
        )
    if not verifier.is_file():
        reasons.append(
            "runner-engine lock verifier is absent"
        )
    if not executor.is_file():
        reasons.append(
            "scientific executor is absent"
        )

    if lock_path.is_file():
        lock = json.loads(
            lock_path.read_text(
                encoding="utf-8"
            )
        )
        if not lock.get(
            "runner_engine_locked",
            False,
        ):
            reasons.append(
                "lock does not authorize execution"
            )
        if lock.get(
            "scientific_simulation_run",
            False,
        ):
            reasons.append(
                "lock is marked post-execution"
            )

    if not reasons and verifier.is_file():
        verification = subprocess.run(
            [sys.executable, str(verifier)],
            check=False,
        )
        if verification.returncode != 0:
            reasons.append(
                "runner-engine verifier failed"
            )

    if reasons:
        print("=" * 80)
        print("D8-A final scientific execution gate")
        print("=" * 80)
        print("Gate state: CLOSED")
        for reason in reasons:
            print(f"- {reason}")
        print("Scientific output root touched: NO")
        print("Scientific simulation run: NO")
        if arguments.execute:
            raise SystemExit(2)
        return

    print("=" * 80)
    print("D8-A final scientific execution gate")
    print("=" * 80)
    print("Gate state: OPEN")
    print("Runner-engine lock verified: YES")

    if not arguments.execute:
        print("Scientific execution requested: NO")
        return

    command = [
        sys.executable,
        str(executor),
        "--execute",
        *remainder,
    ]
    raise SystemExit(
        subprocess.call(command)
    )


if __name__ == "__main__":
    main()
