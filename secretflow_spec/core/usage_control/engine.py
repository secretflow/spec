# Copyright 2025 Ant Group Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Reference usage-control pipeline aligned with TC609 Usage Control Section 7/8.

The pipeline mirrors the normative interaction flow (Section 8.1):

    request -> collect context (a) -> fetch strategies (b) -> verify (c)
            -> sync execution feedback (d) -> execute with obligations (f)
            -> evidence record (g)

``UsageControlEngine`` is the protocol third-party connectors can implement
so that the consistency test-suite in ``tests/test_usage_control.py`` can be
run against their implementation (consistency/conformance testing).
"""

from __future__ import annotations

import abc
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .model import (
    Decision,
    DigitalContract,
    EvidenceRecord,
    UsageContext,
)
from .validator import (
    ValidationError,
    check_obligation_ordering,
    detect_policy_conflicts,
    validate_contract,
    verify_operation,
)


class UsageControlEngine(abc.ABC):
    """Protocol that a policy-execute-point implementation must satisfy.

    The consistency test-suite drives implementations exclusively through
    this interface, so the same tests can certify any connector.
    """

    @abc.abstractmethod
    def load_contract(self, contract: DigitalContract) -> List[str]:
        """Parse and store the contract; return validation errors (7.1.2.2)."""

    @abc.abstractmethod
    def verify(self, context: UsageContext, action: str) -> Tuple[Decision, List[str]]:
        """Behaviour verification for a usage request (7.1.2.3)."""

    @abc.abstractmethod
    def execute(self, context: UsageContext, action: str) -> Tuple[Decision, Dict[str, Any]]:
        """Execute the operation incl. obligations; returns execution report (7.1.2.4)."""

    @abc.abstractmethod
    def evidence(self) -> List[EvidenceRecord]:
        """Return collected evidence records (7.1.3)."""


class ReferenceEngine(UsageControlEngine):
    """Minimal reference implementation used for self-consistency tests.

    It is intentionally small: its purpose is to pin down the normative
    semantics (decision values, default-deny, obligation ordering, evidence
    recording), not to be a production connector.
    """

    def __init__(self, now: Optional[datetime] = None) -> None:
        self._contracts: List[DigitalContract] = []
        self._obligations_executed: Dict[str, List[int]] = {}
        self._evidence: List[EvidenceRecord] = []
        self._now = now or datetime.now(timezone.utc)

    # -- internal helpers ---------------------------------------------------
    def _record(self, stage: str, subject: str, object_ref: str, result: str, details: Dict[str, Any]) -> None:
        self._evidence.append(
            EvidenceRecord(
                stage=stage,
                timestamp=self._now.isoformat(),
                subject=subject,
                object_ref=object_ref,
                result=result,
                details=details,
            )
        )

    def _all_policies(self) -> List[Any]:
        return [p for c in self._contracts for p in c.policies]

    # -- protocol implementation --------------------------------------------
    def load_contract(self, contract: DigitalContract) -> List[str]:
        errors = validate_contract(contract)
        conflicts = detect_policy_conflicts(contract.policies)
        errors.extend(f"conflict({c.kind}): {c.detail}" for c in conflicts)
        self._record(
            stage="strategy_parse",
            subject="platform",
            object_ref=contract.info.contract_id,
            result="parsed" if not errors else "rejected",
            details={"errors": errors, "policy_count": len(contract.policies)},
        )
        if not errors:
            self._contracts.append(contract)
        return errors

    def verify(self, context: UsageContext, action: str) -> Tuple[Decision, List[str]]:
        decision, failed = verify_operation(self._all_policies(), context, action)
        self._record(
            stage="behavior_verify",
            subject=context.subject_id,
            object_ref=f"{context.product_id}:{action}",
            result=decision.value,
            details={"failed_constraints": failed},
        )
        return decision, failed

    def execute(self, context: UsageContext, action: str) -> Tuple[Decision, Dict[str, Any]]:
        decision, failed = self.verify(context, action)
        if decision == Decision.DEFAULT_DENY:
            raise ValidationError(
                f"no applicable policy for product '{context.product_id}' "
                f"and action '{action}' (default deny)"
            )
        if decision == Decision.DENIED:
            return decision, {"executed": False, "failed_constraints": failed}

        obligations = self._pending_obligations(context, action)
        report: Dict[str, Any] = {
            "executed": decision == Decision.ALLOWED,
            "decision": decision.value,
            "obligations": obligations,
        }
        if decision == Decision.CONDITIONAL:
            # 7.1.2.4 b): fulfil prior obligations first, then re-verify.
            orders = [ob["order"] for ob in obligations]
            self._obligations_executed[context.product_id] = sorted(orders)
            decision, failed = self.verify(context, action)
            report["decision_after_obligations"] = decision.value
            report["executed"] = decision == Decision.ALLOWED
        self._record(
            stage="operation_execute",
            subject=context.subject_id,
            object_ref=f"{context.product_id}:{action}",
            result=decision.value,
            details=report,
        )
        return decision, report

    def evidence(self) -> List[EvidenceRecord]:
        return list(self._evidence)

    # -- obligations ---------------------------------------------------------
    def _pending_obligations(self, context: UsageContext, action: str) -> List[Dict[str, Any]]:
        obligations: List[Dict[str, Any]] = []
        for p in self._all_policies():
            if p.policy_type.name != "ALLOW":
                continue
            if not any(o.product_id == context.product_id for o in p.objects):
                continue
            if not any(op.action.value == action for op in p.operations):
                continue
            for ob in p.prior_obligations:
                obligations.append(ob if isinstance(ob, dict) else {"action": str(ob)})
        ordering_errors = check_obligation_ordering(obligations)
        if ordering_errors:
            raise ValidationError("; ".join(ordering_errors))
        return obligations
