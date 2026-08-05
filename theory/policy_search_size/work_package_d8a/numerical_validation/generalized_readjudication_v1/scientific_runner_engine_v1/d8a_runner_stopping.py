from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StoppingDecision:
    stop: bool
    reason: str
    next_batch_size: int


@dataclass(frozen=True)
class StoppingSchedule:
    initial_replicates: int
    batch_size: int
    maximum_replicates: int

    def __post_init__(self) -> None:
        if self.initial_replicates < 1:
            raise ValueError(
                "initial_replicates must be positive"
            )
        if self.batch_size < 1:
            raise ValueError(
                "batch_size must be positive"
            )
        if (
            self.maximum_replicates
            < self.initial_replicates
        ):
            raise ValueError(
                "maximum_replicates must not be "
                "smaller than initial_replicates"
            )

    def decide(
        self,
        completed_replicates: int,
        *,
        precision_pass: bool,
    ) -> StoppingDecision:
        completed = int(completed_replicates)
        if completed < 0:
            raise ValueError(
                "completed_replicates must be nonnegative"
            )

        if completed >= self.maximum_replicates:
            return StoppingDecision(
                stop=True,
                reason="maximum_replicates_reached",
                next_batch_size=0,
            )

        if (
            completed >= self.initial_replicates
            and precision_pass
        ):
            return StoppingDecision(
                stop=True,
                reason="precision_target_met",
                next_batch_size=0,
            )

        remaining = (
            self.maximum_replicates
            - completed
        )
        if completed < self.initial_replicates:
            required = (
                self.initial_replicates
                - completed
            )
            next_batch = min(
                max(self.batch_size, required),
                remaining,
            )
            reason = (
                "initial_replicates_incomplete"
            )
        else:
            next_batch = min(
                self.batch_size,
                remaining,
            )
            reason = (
                "precision_target_not_met"
            )

        return StoppingDecision(
            stop=False,
            reason=reason,
            next_batch_size=next_batch,
        )


@dataclass(frozen=True)
class RoleAwarePrecisionOnlyStoppingRule:
    primary: StoppingSchedule
    diagnostic: StoppingSchedule

    def schedule_for(
        self,
        class_role: str,
    ) -> StoppingSchedule:
        role = str(class_role)
        if role == "primary":
            return self.primary
        if role == "diagnostic":
            return self.diagnostic
        raise ValueError(
            f"unknown class role: {role}"
        )

    def decide(
        self,
        class_role: str,
        completed_replicates: int,
        *,
        precision_pass: bool,
    ) -> StoppingDecision:
        return self.schedule_for(
            class_role
        ).decide(
            completed_replicates,
            precision_pass=precision_pass,
        )
