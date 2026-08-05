from __future__ import annotations

import hashlib

import numpy as np


MASTER_SEED = 20260804


def canonical_class_key(
    class_record: dict[str, object],
) -> str:
    return "|".join(
        [
            str(class_record["dependence"]),
            f"{float(class_record['candidate_probability']):.12f}",
            f"{float(class_record['trigger_probability']):.12f}",
        ]
    )


def _spawn_words(text: str) -> tuple[int, int, int, int]:
    digest = hashlib.sha256(
        text.encode("utf-8")
    ).digest()
    return tuple(
        int.from_bytes(
            digest[index : index + 4],
            byteorder="little",
            signed=False,
        )
        for index in range(0, 16, 4)
    )


def seed_sequence(
    class_record: dict[str, object],
    stream_name: str,
    replicate_index: int = 0,
    *,
    master_seed: int = MASTER_SEED,
) -> np.random.SeedSequence:
    if replicate_index < 0:
        raise ValueError(
            "replicate_index must be nonnegative"
        )
    key = canonical_class_key(class_record)
    words = _spawn_words(
        f"{key}|{stream_name}"
    )
    return np.random.SeedSequence(
        entropy=master_seed,
        spawn_key=(
            *words,
            int(replicate_index),
        ),
    )


def make_rng(
    class_record: dict[str, object],
    stream_name: str,
    replicate_index: int = 0,
    *,
    master_seed: int = MASTER_SEED,
) -> np.random.Generator:
    return np.random.Generator(
        np.random.PCG64DXSM(
            seed_sequence(
                class_record,
                stream_name,
                replicate_index,
                master_seed=master_seed,
            )
        )
    )
