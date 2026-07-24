#!/usr/bin/env python3
"""Fast structural checks for the Phase 3C candidate libraries."""
from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "pipeline_candidate_count_phase3c.py"
spec = importlib.util.spec_from_file_location("phase3c_runner", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

for library in module.LIBRARIES:
    first = module.build_library(library, seed=123)
    second = module.build_library(library, seed=123)
    assert len(first) == 20, (library, len(first))
    assert len(set(first)) == 20, library
    assert tuple(first) == tuple(second), library
    assert len(tuple(first)[:7]) == 7
    for name, estimator in first.items():
        assert hasattr(estimator, "fit"), (library, name)
        estimator.get_params(deep=True)
    print(f"PASS: {library}: 20 unique candidates; K7 is the first 7; deterministic names")
print("ALL PHASE 3C LIBRARY CHECKS PASSED")
