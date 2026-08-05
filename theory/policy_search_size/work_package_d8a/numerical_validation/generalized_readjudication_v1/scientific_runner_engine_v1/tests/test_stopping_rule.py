from __future__ import annotations

import json
import unittest
from pathlib import Path

from d8a_runner_stopping import (
    RoleAwarePrecisionOnlyStoppingRule,
    StoppingSchedule,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads(
    (
        ROOT
        / "D8A_LOCKED_MONTE_CARLO_CONTRACT.json"
    ).read_text(encoding="utf-8")
)
SCHEDULES = CONTRACT[
    "normalized_schedules"
]


def make_rule() -> (
    RoleAwarePrecisionOnlyStoppingRule
):
    return RoleAwarePrecisionOnlyStoppingRule(
        primary=StoppingSchedule(
            **SCHEDULES["primary"]
        ),
        diagnostic=StoppingSchedule(
            **SCHEDULES["diagnostic"]
        ),
    )


class StoppingRuleTests(unittest.TestCase):
    def test_primary_initial_stage_continues(
        self,
    ) -> None:
        rule = make_rule()
        decision = rule.decide(
            "primary",
            0,
            precision_pass=True,
        )
        self.assertFalse(decision.stop)

    def test_diagnostic_initial_stage_continues(
        self,
    ) -> None:
        rule = make_rule()
        decision = rule.decide(
            "diagnostic",
            0,
            precision_pass=True,
        )
        self.assertFalse(decision.stop)

    def test_primary_precision_pass_stops(
        self,
    ) -> None:
        rule = make_rule()
        decision = rule.decide(
            "primary",
            rule.primary.initial_replicates,
            precision_pass=True,
        )
        self.assertTrue(decision.stop)
        self.assertEqual(
            decision.reason,
            "precision_target_met",
        )

    def test_diagnostic_maximum_stops(
        self,
    ) -> None:
        rule = make_rule()
        decision = rule.decide(
            "diagnostic",
            rule.diagnostic.maximum_replicates,
            precision_pass=False,
        )
        self.assertTrue(decision.stop)
        self.assertEqual(
            decision.reason,
            "maximum_replicates_reached",
        )

    def test_batch_is_clamped(self) -> None:
        rule = make_rule()
        schedule = rule.primary
        decision = rule.decide(
            "primary",
            schedule.maximum_replicates - 1,
            precision_pass=False,
        )
        self.assertEqual(
            decision.next_batch_size,
            1,
        )

    def test_unknown_role_raises(self) -> None:
        rule = make_rule()
        with self.assertRaises(ValueError):
            rule.decide(
                "unknown",
                0,
                precision_pass=False,
            )


if __name__ == "__main__":
    unittest.main()
