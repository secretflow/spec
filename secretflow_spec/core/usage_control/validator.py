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
"""Validation and behaviour-verification logic aligned with TC609 clauses.

Clause traceability (see README.md for the full matrix):

- Digital Contract Requirements 7.1 c)  -> ``validate_contract`` core-field
  completeness check (auto validation at creation time).
- Digital Contract Requirements 7.2.1 contractId composition -> ``ContractId``
  format checker (47-char composite identifier, Usage Control Table 2).
- Digital Contract Requirements 6.2.2 -> policy-type extension rules
  (allow->prior obligation, forbid->remedial measure, obligation->liability).
- Usage Control 7.1.2.2 d) -> ``detect_policy_conflicts`` (authorization
  conflict, contradictory constraints, scope inconsistency).
- Usage Control 7.1.2.3 a)-c) -> ``ReferenceEngine.verify`` (context
  collection, condition verification, explicit decision).
- Usage Control 7.1.2.4 e) -> ``check_obligation_ordering``.
- Usage Control 7.1.2.4 i) -> ``validate_policy_inheritance``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .model import (
    Constraint,
    ConstraintName,
    ContractObject,
    ContractPolicy,
    ContractInfo,
    Decision,
    DigitalContract,
    Operator,
    PolicyType,
    UsageContext,
)


class ValidationError(Exception):
    """Raised when a contract or policy violates a structural requirement."""


# ---------------------------------------------------------------------------
# Contract identifier (Usage Control Table 2 / Digital Contract 7.2.1)
# ---------------------------------------------------------------------------

CONTRACT_ID_TOTAL_LEN = 47
CONTRACT_ID_COMPOSITION = {
    "type_code": (0, 1),
    "node_type_code": (1, 2),
    "subject_code": (2, 20),
    "region_industry_code": (20, 24),
    "time_code": (24, 38),
    "random_code": (38, 46),
    "check_code": (46, 47),
}

_STRATEGY_ID_LEN = 36
_CONNECTOR_ID_LEN = 32


def check_contract_id_format(contract_id: str) -> List[str]:
    """Validate the 47-character composite contract identifier.

    Returns a list of error descriptions; empty list means valid.
    """
    errors: List[str] = []
    if not isinstance(contract_id, str):
        return ["contract_id must be a string"]
    if len(contract_id) != CONTRACT_ID_TOTAL_LEN:
        errors.append(
            f"contract_id length {len(contract_id)} != {CONTRACT_ID_TOTAL_LEN}"
        )
        return errors
    time_code = contract_id[CONTRACT_ID_COMPOSITION["time_code"][0]:CONTRACT_ID_COMPOSITION["time_code"][1]]
    try:
        datetime.strptime(time_code, "%Y%m%d%H%M%S")
    except ValueError:
        errors.append(f"contract_id time_code '{time_code}' is not YYYYMMDDHHMMSS")
    if not contract_id[:24].isdigit():
        # type/node/subject/region parts are digit codes per the standard table
        errors.append("contract_id type/node/subject/region codes must be digits")
    if not contract_id[38:46].isalnum():
        errors.append("contract_id random_code must be alphanumeric")
    if not contract_id[46].isdigit():
        errors.append("contract_id check_code must be a digit")
    return errors


# ---------------------------------------------------------------------------
# Contract-level validation (Digital Contract 7.1 c) & 6.2.x)
# ---------------------------------------------------------------------------

_REQUIRED_POLICY_EXTENSIONS = {
    PolicyType.ALLOW: "prior_obligations",
    PolicyType.FORBID: "remedial_measures",
    PolicyType.OBLIGATION: "liability",
}


def validate_contract(contract: DigitalContract) -> List[str]:
    """Structural validation of a digital contract.

    Implements the "core field completeness auto-check" required by Digital
    Contract Requirements 7.1 c) and the composition rules of 6.2.1/6.2.2.
    Returns the list of violations (empty = valid).
    """
    errors: List[str] = []
    info: ContractInfo = contract.info
    if not info.contract_id:
        errors.append("contract_info.contract_id is required (表1#1)")
    else:
        errors.extend(f"contract_id: {e}" for e in check_contract_id_format(info.contract_id))
    if not info.contract_name:
        errors.append("contract_info.contract_name is required (表1#2)")
    if not info.subject_ids:
        errors.append("contract_info.subject_ids is required (表1#7)")
    if not (info.subject_ids and info.signatures):
        errors.append(
            "contract_info.signatures required: parties must confirm the "
            "contract by digital signature (表1#11, 7.2 b))"
        )
    if not contract.policies:
        errors.append("at least one contract policy is required (6.1)")
    for i, policy in enumerate(contract.policies):
        errors.extend(f"policies[{i}]: {e}" for e in validate_policy(policy))
    return errors


def validate_policy(policy: ContractPolicy) -> List[str]:
    """Validate one contract policy instance (6.2.2 composition rules)."""
    errors: List[str] = []
    if not policy.strategy_id:
        errors.append("strategy_id is required (使用控制 表2#2)")
    elif len(policy.strategy_id) != _STRATEGY_ID_LEN:
        errors.append(
            f"strategy_id length {len(policy.strategy_id)} != {_STRATEGY_ID_LEN} "
            "(使用控制 表2: 策略实例唯一标识 36 位)"
        )
    if not policy.objects:
        errors.append("policy.objects is required (6.2.2.1 标的信息)")
    if not policy.operations:
        errors.append("policy.operations is required (6.2.2.3 操作行为)")
    ext_field = _REQUIRED_POLICY_EXTENSIONS[policy.policy_type]
    if policy.policy_type == PolicyType.ALLOW and policy.prior_obligations is None:
        errors.append(f"ALLOW policy requires {ext_field} extension (6.2.2 扩展信息)")
    if policy.policy_type == PolicyType.FORBID and not policy.remedial_measures:
        errors.append("FORBID policy requires remedial_measures extension (6.2.2)")
    if policy.policy_type == PolicyType.OBLIGATION and policy.liability is None:
        errors.append("OBLIGATION policy requires liability extension (6.2.2)")
    for j, op in enumerate(policy.operations):
        for k, c in enumerate(op.constraints):
            if isinstance(c.name, str) and c.name not in _KNOWN_CONSTRAINT_NAMES():
                errors.append(
                    f"operations[{j}].constraints[{k}]: unknown constraint name "
                    f"'{c.name}' must use name='extend' (表6.1#17 可扩展性)"
                )
    return errors


def _KNOWN_CONSTRAINT_NAMES() -> List[str]:
    return [c.value for c in ConstraintName]


# ---------------------------------------------------------------------------
# Conflict detection (Usage Control 7.1.2.2 d)
# ---------------------------------------------------------------------------

@dataclass
class PolicyConflict:
    kind: str  # authorization | contradictory | scope_inconsistent
    detail: str
    policy_ids: Tuple[str, str]


def detect_policy_conflicts(policies: List[ContractPolicy]) -> List[PolicyConflict]:
    """Detect conflicts among multiple policies (Usage Control 7.1.2.2 d).

    Three categories required by the clause:
    - authorization conflict: same object+operation simultaneously ALLOW and
      FORBID;
    - contradictory constraints: same object+operation carries mutually
      exclusive numeric constraints (e.g. count lteq 100 vs count gt 100);
    - scope inconsistency: same strategy_id reused by different policies.
    """
    conflicts: List[PolicyConflict] = []

    def signature(op_action: str, product_id: str) -> str:
        return f"{op_action}@{product_id}"

    allow_map: Dict[str, str] = {}
    numeric_constraints: Dict[str, List[Tuple[Constraint, str]]] = {}
    for p in policies:
        seen_in_policy = set()
        for obj in p.objects:
            for op in p.operations:
                sig = signature(op.action.value, obj.product_id)
                if sig in seen_in_policy:
                    conflicts.append(
                        PolicyConflict(
                            "scope_inconsistent",
                            f"duplicate operation '{sig}' within one policy",
                            (p.strategy_id, p.strategy_id),
                        )
                    )
                seen_in_policy.add(sig)
                if p.policy_type == PolicyType.ALLOW:
                    if sig in allow_map:
                        continue
                    allow_map[sig] = p.strategy_id
                elif p.policy_type == PolicyType.FORBID:
                    if sig in allow_map:
                        conflicts.append(
                            PolicyConflict(
                                "authorization",
                                f"operation '{sig}' is both allowed "
                                f"({allow_map[sig]}) and forbidden ({p.strategy_id})",
                                (allow_map[sig], p.strategy_id),
                            )
                        )
                for c in op.constraints:
                    if isinstance(c.value, (int, float)):
                        numeric_constraints.setdefault(sig, []).append((c, p.strategy_id))

    # contradictory numeric constraints on the same operation signature
    _CONTRADICTORY_PAIRS = {
        (Operator.LTEQ, Operator.GT),
        (Operator.LT, Operator.GTEQ),
        (Operator.EQ, Operator.NEQ),
        (Operator.EQ, Operator.GT),
        (Operator.EQ, Operator.LT),
    }
    for sig, items in numeric_constraints.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                c1, p1 = items[i]
                c2, p2 = items[i + 1]
                if c1.name == c2.name and (c1.operator, c2.operator) in _CONTRADICTORY_PAIRS:
                    conflicts.append(
                        PolicyConflict(
                            "contradictory",
                            f"operation '{sig}' constraint {c1.name.value}: "
                            f"{c1.operator.value} {c1.value} vs {c2.operator.value} {c2.value}",
                            (p1, p2),
                        )
                    )
    return conflicts


# ---------------------------------------------------------------------------
# Behaviour verification engine primitives (Usage Control 7.1.2.3)
# ---------------------------------------------------------------------------

def _as_float(v: Any) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def evaluate_constraint(constraint: Constraint, context: UsageContext) -> bool:
    """Evaluate a single constraint against the context (7.1.2.3 b).

    Implements the 12 operators of Digital Contract Table 7.2. Unknown context
    values fail closed (deny), which matches the "default deny" posture.
    """
    actual = context.get(constraint.name.value)
    if actual is None:
        return False
    expected = constraint.value
    op = constraint.operator
    if op == Operator.EQ:
        return str(actual) == str(expected)
    if op == Operator.NEQ:
        return str(actual) != str(expected)
    a, b = _as_float(actual), _as_float(expected)
    if op in (Operator.GT, Operator.GTEQ, Operator.LT, Operator.LTEQ):
        if a is None or b is None:
            return False
        return {
            Operator.GT: a > b,
            Operator.GTEQ: a >= b,
            Operator.LT: a < b,
            Operator.LTEQ: a <= b,
        }[op]
    expected_list = expected if isinstance(expected, list) else [expected]
    actual_str = str(actual)
    expected_strs = [str(x) for x in expected_list]
    if op == Operator.IS_ANY_OF:
        return actual_str in expected_strs
    if op == Operator.IS_NONE_OF:
        return actual_str not in expected_strs
    if op == Operator.IS_ALL_OF:
        return isinstance(actual, (list, tuple)) and set(map(str, actual)) == set(expected_strs)
    if op == Operator.IS_A:
        # "belongs to an instance/type of the constraint value"; for CIDR
        # notation the membership check is exact (Appendix D scenario 1/5).
        for s in expected_strs:
            if s == actual_str:
                return True
            if "/" in s:
                try:
                    import ipaddress

                    return ipaddress.ip_address(actual) in ipaddress.ip_network(s, strict=False)
                except (ValueError, TypeError):
                    continue
        return False
    if op == Operator.HAS_PART:
        return any(s in actual_str for s in expected_strs)
    if op == Operator.IS_PART_OF:
        return any(actual_str in s for s in expected_strs)
    return False


def find_applicable_policies(
    policies: List[ContractPolicy], context: UsageContext
) -> List[ContractPolicy]:
    """Return policies whose object list covers ``context.product_id``."""
    return [
        p for p in policies if any(o.product_id == context.product_id for o in p.objects)
    ]


def verify_operation(
    policies: List[ContractPolicy],
    context: UsageContext,
    action: str,
) -> Tuple[Decision, List[str]]:
    """Verify one data-usage request (Usage Control 7.1.2.3 a-c).

    Returns ``(decision, failed_constraint_refs)``. Decision semantics:

    - no policy covers the (product, action) pair -> ``DEFAULT_DENY``;
    - a FORBID policy matches, or any ALLOW/OBLIGATION constraint fails ->
      ``DENIED``;
    - all constraints pass and the matched ALLOW policy carries pending prior
      obligations -> ``CONDITIONAL``;
    - all constraints pass with no pending obligations -> ``ALLOWED``.
    """
    applicable = find_applicable_policies(policies, context)
    for p in applicable:
        for op in p.operations:
            if op.action.value != action:
                continue
            if p.policy_type == PolicyType.FORBID:
                return Decision.DENIED, [f"forbid-policy:{p.strategy_id}"]
    relevant = [p for p in applicable if p.policy_type in (PolicyType.ALLOW, PolicyType.OBLIGATION)]
    if not relevant:
        return Decision.DEFAULT_DENY, []
    failed: List[str] = []
    has_pending_obligation = False
    for p in relevant:
        for op in p.operations:
            if op.action.value != action:
                continue
            for c in op.constraints:
                if not evaluate_constraint(c, context):
                    failed.append(f"{p.strategy_id}:{c.name.value} {c.operator.value} {c.value!r}")
        if p.prior_obligations:
            has_pending_obligation = True
    if failed:
        return Decision.DENIED, failed
    if has_pending_obligation:
        return Decision.CONDITIONAL, []
    return Decision.ALLOWED, []


# ---------------------------------------------------------------------------
# Obligation ordering (Usage Control 7.1.2.4 e)
# ---------------------------------------------------------------------------

def check_obligation_ordering(obligations: List[Dict[str, Any]]) -> List[str]:
    """Validate that declared obligation steps carry a strict, complete order.

    Clause 7.1.2.4 e) requires "严格保证各操作的执行顺序" for extra pre /
    parallel / post operations (second authentication, watermarking,
    burn-after-delete, behaviour notification...). Each obligation dict must
    expose a unique positive integer ``order`` and a non-empty ``action``.
    """
    errors: List[str] = []
    orders: List[int] = []
    for i, ob in enumerate(obligations):
        if not ob.get("action"):
            errors.append(f"obligations[{i}].action is required")
        order = ob.get("order")
        if not isinstance(order, int) or order <= 0:
            errors.append(f"obligations[{i}].order must be a positive integer")
        else:
            orders.append(order)
    if len(orders) != len(set(orders)):
        errors.append("obligation orders must be unique (strict sequence, 7.1.2.4 e)")
    return errors


# ---------------------------------------------------------------------------
# Policy inheritance (Usage Control 7.1.2.4 i)
# ---------------------------------------------------------------------------

def validate_policy_inheritance(
    parent: ContractPolicy, derived: ContractPolicy
) -> List[str]:
    """Check that a derived product keeps the parent's control constraints.

    Clause 7.1.2.4 i): intermediate data and results derived from the product
    must remain bound to the same usage-control policies.
    """
    errors: List[str] = []
    parent_pairs = {
        (op.action.value, (c.name.value, c.operator.value, str(c.value)))
        for op in parent.operations
        for c in op.constraints
    }
    derived_pairs = {
        (op.action.value, (c.name.value, c.operator.value, str(c.value)))
        for op in derived.operations
        for c in op.constraints
    }
    missing = parent_pairs - derived_pairs
    for action, constraint in sorted(missing):
        errors.append(
            f"derived product loses inherited constraint '{constraint[0]}' "
            f"on operation '{action}' (7.1.2.4 i)"
        )
    return errors
