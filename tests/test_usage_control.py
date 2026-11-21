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
"""Consistency test-suite for TC609 trusted-data-space usage control.

Two layers:

1. **Clause-derived consistency cases** (``TC-*``): executable translations of
   individual requirements from the public technical documents —
   *Trusted Data Space: Digital Contract Requirements* (DC), *Trusted Data
   Space: Usage Control Requirements* (UC) and *Trusted Data Space: Technical
   Capability Evaluation Specification* (EV). Each test's docstring cites the
   clause it enforces; the full clause->test matrix lives in
   ``secretflow_spec/core/usage_control/README.md``.

2. **A reusable conformance driver** (``run_consistency_suite``): runs the
   same behaviour checks against ANY implementation of
   ``UsageControlEngine`` (reference engine included), so connector teams can
   certify their implementation by pointing the suite at their engine.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pytest

from secretflow_spec.core.usage_control import (
    Constraint,
    ConstraintName,
    ContractInfo,
    ContractObject,
    ContractPolicy,
    Decision,
    DigitalContract,
    Operation,
    OperationAction,
    Operator,
    PolicyExecutePoint,
    PolicyType,
    ReferenceEngine,
    UsageContext,
    UsageControlEngine,
    ValidationError,
    check_contract_id_format,
    check_obligation_ordering,
    detect_policy_conflicts,
    validate_contract,
    validate_policy_inheritance,
    verify_operation,
)

EXAMPLES_DIR = Path(__file__).parent.parent / "secretflow_spec" / "core" / "usage_control" / "examples"
SCHEMA_PATH = (
    Path(__file__).parent.parent
    / "secretflow_spec"
    / "core"
    / "usage_control"
    / "schema"
    / "digital_contract.schema.json"
)

VALID_CONTRACT_ID = "10110000000000000001310020250601120000AB12CD347"


# ---------------------------------------------------------------------------
# builders
# ---------------------------------------------------------------------------

def _obj(pid: str = "DP-001") -> ContractObject:
    return ContractObject(product_id=pid, product_name="demo", owner_id="P-1")


def _pep() -> PolicyExecutePoint:
    return PolicyExecutePoint(provider_pep_id="C" * 32, consumer_pep_id="D" * 32)


def make_allow_policy(
    product_id: str = "DP-001",
    action: OperationAction = OperationAction.READ,
    constraints: List[Constraint] | None = None,
    prior_obligations: List[dict] | None = None,
    strategy_id: str = "0f1e2d3c-4b5a-6978-8796-a5b4c3d2e1f0",
) -> ContractPolicy:
    return ContractPolicy(
        policy_type=PolicyType.ALLOW,
        strategy_id=strategy_id,
        objects=[_obj(product_id)],
        execute_points=[_pep()],
        operations=[Operation(action=action, constraints=constraints or [])],
        prior_obligations=prior_obligations or [],
    )


def make_contract(policies: List[ContractPolicy]) -> DigitalContract:
    return DigitalContract(
        info=ContractInfo(
            contract_id=VALID_CONTRACT_ID,
            contract_name="demo contract",
            subject_ids=["P-1", "C-1"],
            subject_types=["provider", "consumer"],
            signatures={"P-1": "sigP", "C-1": "sigC"},
            valid_until="2026-01-01T00:00:00+08:00",
        ),
        policies=policies,
    )


def make_context(**overrides) -> UsageContext:
    base = dict(
        subject_id="C-1",
        product_id="DP-001",
        connector_id="D" * 32,
        application_id="APP-1",
        operation="read",
        request_time="2025-06-01T10:00:00+08:00",
        location="203.0.113.10",
        environment="data-sandbox",
    )
    base.update(overrides)
    return UsageContext(**base)


# ---------------------------------------------------------------------------
# TC-DC-*: Digital Contract Requirements
# ---------------------------------------------------------------------------

class TestDigitalContractClauses:
    def test_tc_dc_01_contract_id_composition(self):
        """DC 7.2.1 / UC Table 2 #1: 47-char composite contract identifier."""
        ok = VALID_CONTRACT_ID
        assert check_contract_id_format(ok) == []
        for bad in [ok[:-1], ok + "9", ok[:24] + "abcdefgh" + ok[32:]]:
            assert check_contract_id_format(bad), f"expected rejection: {bad}"

    def test_tc_dc_02_core_field_completeness(self):
        """DC 7.1 c): creation auto-check of core fields must reject
        contracts missing id/signature/policies."""
        contract = make_contract([make_allow_policy()])
        assert validate_contract(contract) == []

        broken = make_contract([])
        broken.info.contract_id = ""
        broken.info.signatures = {}
        errors = validate_contract(broken)
        assert any("contract_id" in e for e in errors)
        assert any("signatures" in e for e in errors)
        assert any("at least one contract policy" in e for e in errors)

    def test_tc_dc_03_policy_type_extensions(self):
        """DC 6.2.2: allow->prior obligation, forbid->remedial measure,
        obligation->liability extension requirements."""
        forbid = ContractPolicy(
            policy_type=PolicyType.FORBID,
            strategy_id="a" * 36,
            objects=[_obj()],
            operations=[Operation(action=OperationAction.COPY)],
            remedial_measures=[],
        )
        assert any("remedial_measures" in e for e in validate_contract(make_contract([forbid])))

        obligation = ContractPolicy(
            policy_type=PolicyType.OBLIGATION,
            strategy_id="b" * 36,
            objects=[_obj()],
            operations=[Operation(action=OperationAction.ACCEPT_TRACKING)],
            liability=None,
        )
        assert any("liability" in e for e in validate_contract(make_contract([obligation])))

    def test_tc_dc_04_operation_and_constraint_vocabularies(self):
        """DC Table 4 / Table 6.1 / Table 7.2: operations, constraint names and
        operators must come from the normative vocabularies; unknown constraint
        names must use 'extend'."""
        policy = make_allow_policy(
            constraints=[
                Constraint(name=ConstraintName.COUNT, operator=Operator.LTEQ, value=100),
                Constraint(name="timeInterval", operator=Operator.EQ, value="P1D"),
            ]
        )
        errors = validate_contract(make_contract([policy]))
        assert any("unknown constraint name 'timeInterval'" in e for e in errors)


# ---------------------------------------------------------------------------
# TC-UC-*: Usage Control Requirements
# ---------------------------------------------------------------------------

class TestUsageControlClauses:
    def test_tc_uc_01_decision_vocabulary(self):
        """UC 7.1.2.3 c): decisions must be one of allowed / conditional /
        denied / default_denied."""
        assert {d.value for d in Decision} == {
            "allowed",
            "conditional",
            "denied",
            "default_denied",
        }

    def test_tc_uc_02_default_deny(self):
        """UC 7.1.2.3: request outside any policy scope -> default deny."""
        policies = [make_allow_policy(product_id="DP-001")]
        decision, _ = verify_operation(policies, make_context(product_id="DP-999"), "read")
        assert decision == Decision.DEFAULT_DENY

    def test_tc_uc_03_constraint_verification_pass(self):
        """UC 7.1.2.3 b): all constraint conditions verified per request."""
        policies = [
            make_allow_policy(
                constraints=[
                    Constraint(name=ConstraintName.COUNT, operator=Operator.LTEQ, value=10000),
                    Constraint(name=ConstraintName.NETWORK_ADDRESS, operator=Operator.IS_A, value="203.0.113.0/24"),
                    Constraint(name=ConstraintName.EXECUTION_ENV, operator=Operator.IS_A, value="data-sandbox"),
                ]
            )
        ]
        decision, failed = verify_operation(
            policies, make_context(attributes={"count": 100}), "read"
        )
        assert decision == Decision.ALLOWED, failed

    def test_tc_uc_04_constraint_verification_fail(self):
        """UC 7.1.2.3 b)/c): constraint violation -> explicit deny with refs."""
        policies = [
            make_allow_policy(
                constraints=[
                    Constraint(name=ConstraintName.COUNT, operator=Operator.LTEQ, value=100)
                ]
            )
        ]
        ctx = make_context(attributes={"count": 500})
        decision, failed = verify_operation(policies, ctx, "read")
        assert decision == Decision.DENIED
        assert failed and failed[0].startswith("0f1e2d3c-4b5a-6978-8796-a5b4c3d2e1f0:count")

    def test_tc_uc_05_forbid_overrides_allow(self):
        """UC 7.1.2.2 d)/7.1.2.3: authorization conflict semantics — a FORBID
        policy on the same object+operation must veto access."""
        allow = make_allow_policy(action=OperationAction.COPY)
        forbid = ContractPolicy(
            policy_type=PolicyType.FORBID,
            strategy_id="1" * 36,
            objects=[_obj()],
            execute_points=[_pep()],
            operations=[Operation(action=OperationAction.COPY)],
            remedial_measures=[{"action": "alert"}],
        )
        conflicts = detect_policy_conflicts([allow, forbid])
        assert any(c.kind == "authorization" for c in conflicts)
        decision, _ = verify_operation([allow, forbid], make_context(), "copy")
        assert decision == Decision.DENIED

    def test_tc_uc_06_obligation_ordering_strict(self):
        """UC 7.1.2.4 e): extra pre/parallel/post operations must keep a
        strict execution order."""
        assert check_obligation_ordering([{"action": "log", "order": 1}, {"action": "inform", "order": 2}]) == []
        assert check_obligation_ordering([{"action": "log", "order": 1}, {"action": "log", "order": 1}])
        assert check_obligation_ordering([{"action": "log", "order": 0}])
        assert check_obligation_ordering([{"action": ""}])

    def test_tc_uc_07_policy_inheritance(self):
        """UC 7.1.2.4 i): derived products stay bound to parent constraints."""
        parent = make_allow_policy(
            constraints=[Constraint(name=ConstraintName.COUNT, operator=Operator.LTEQ, value=100)]
        )
        derived_same = make_allow_policy(
            constraints=[Constraint(name=ConstraintName.COUNT, operator=Operator.LTEQ, value=100)]
        )
        derived_lossy = make_allow_policy(constraints=[])
        assert validate_policy_inheritance(parent, derived_same) == []
        assert any("loses inherited constraint" in e for e in validate_policy_inheritance(parent, derived_lossy))

    def test_tc_uc_08_strategy_id_length(self):
        """UC Table 2 #2/#3: strategyId / strategyVersion are 36-char fields."""
        policy = make_allow_policy(strategy_id="short")
        assert any("strategy_id" in e for e in validate_contract(make_contract([policy])))


# ---------------------------------------------------------------------------
# EV-*: Technical Capability Evaluation Specification checkpoints
# ---------------------------------------------------------------------------

class TestEvaluationCheckpoints:
    def _engine_with_contract(self) -> ReferenceEngine:
        engine = ReferenceEngine()
        contract = make_contract(
            [
                make_allow_policy(
                    constraints=[
                        Constraint(name=ConstraintName.EXECUTION_ENV, operator=Operator.IS_A, value="data-sandbox")
                    ],
                    prior_obligations=[{"action": "log", "order": 1}],
                )
            ]
        )
        errors = engine.load_contract(contract)
        assert errors == []
        return engine

    def test_ev_uc_a_usage_environment_isolation(self):
        """EV Table 18 a) 数据使用环境: sandbox/scoped environment constraint
        is enforced at request time."""
        engine = self._engine_with_contract()
        decision, _ = engine.verify(make_context(environment="bare-metal"), "read")
        assert decision == Decision.DENIED
        decision, _ = engine.verify(make_context(environment="data-sandbox"), "read")
        assert decision == Decision.CONDITIONAL  # pending prior obligation

    def test_ev_uc_c_control_policy_execution(self):
        """EV Table 18 c) 控制策略执行能力: real-time verification with
        violation blocking; obligations gate the final allow."""
        engine = self._engine_with_contract()
        decision, report = engine.execute(make_context(), "read")
        assert decision == Decision.CONDITIONAL
        assert report["obligations"][0]["action"] == "log"
        decision, _ = engine.verify(make_context(), "read")
        assert decision == Decision.CONDITIONAL

    def test_ev_uc_d_usage_evidence(self):
        """EV Table 18 d) 使用存证能力: full-pipeline evidence records with
        stage/time/subject/object/result."""
        engine = self._engine_with_contract()
        engine.execute(make_context(), "read")
        stages = [e.stage for e in engine.evidence()]
        assert stages[0] == "strategy_parse"
        assert "behavior_verify" in stages
        assert "operation_execute" in stages
        for e in engine.evidence():
            assert e.timestamp and e.subject and e.object_ref and e.result

    def test_ev_dc_a_integrity_and_b_authenticity_rejections(self):
        """EV Table 19 a)/b): tampered or unsigned contracts are rejected at
        parse stage (数字合约完整性/真实性保障能力)."""
        engine = ReferenceEngine()
        contract = make_contract([make_allow_policy()])
        # tamper the 14-digit time code -> structurally invalid identifier
        contract.info.contract_id = contract.info.contract_id[:24] + "9" * 14 + contract.info.contract_id[38:]
        errors = engine.load_contract(contract)
        assert errors and "contract_id" in errors[0]
        assert engine.evidence()[-1].result == "rejected"

        # EV Table 19 b) authenticity: missing party signatures must be rejected
        engine2 = ReferenceEngine()
        unsigned = make_contract([make_allow_policy()])
        unsigned.info.signatures = {}
        errors = engine2.load_contract(unsigned)
        assert errors and any("signatures" in e for e in errors)


# ---------------------------------------------------------------------------
# Example fixtures validate against the normative JSON Schema
# ---------------------------------------------------------------------------

class TestExamplesConformance:
    def test_examples_against_json_schema(self):
        jsonschema = pytest.importorskip("jsonschema")
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        for path in sorted(EXAMPLES_DIR.glob("scenario*.json")):
            instance = json.loads(path.read_text(encoding="utf-8"))
            errors = sorted(validator.iter_errors(instance), key=lambda e: e.json_path)
            assert not errors, f"{path.name}: " + "; ".join(
                f"{e.json_path}: {e.message}" for e in errors
            )

    def test_examples_accepted_by_reference_engine(self):
        """Round-trip: every Appendix-D scenario example loads cleanly."""
        from secretflow_spec.core.usage_control.model import (
            ContractObject as CO,
            ContractPolicy as CP,
            ContractInfo as CI,
            DigitalContract as DC,
            Operation as OP,
            OperationAction as OA,
            Operator as OPX,
            PolicyExecutePoint as PEP,
            PolicyType as PT,
        )
        from secretflow_spec.core.usage_control.validator import validate_contract

        name_to_action = {a.value: a for a in OA}
        for path in sorted(EXAMPLES_DIR.glob("scenario*.json")):
            raw = json.loads(path.read_text(encoding="utf-8"))
            info = raw["contractInfo"]
            policies = []
            for p in raw["contractPolicies"]:
                ops = [
                    OP(
                        action=name_to_action[o["action"]],
                        constraints=[
                            Constraint(
                                name=ConstraintName(c["name"])
                                if c["name"] in ConstraintName._value2member_map_
                                else ConstraintName.EXTEND,
                                operator=OPX(c["operator"]),
                                value=c["value"],
                            )
                            for c in o.get("constraints", [])
                        ],
                    )
                    for o in p["operations"]
                ]
                policies.append(
                    CP(
                        policy_type=PT(p["policyType"]),
                        strategy_id=p["strategyId"],
                        objects=[CO(product_id=o["productId"], product_name=o["productName"], owner_id=o.get("ownerId", "")) for o in p["objects"]],
                        execute_points=[PEP(provider_pep_id=e["providerPepId"], consumer_pep_id=e.get("consumerPepId", "")) for e in p.get("executePoints", [])],
                        operations=ops,
                        prior_obligations=p.get("priorObligations", []),
                        remedial_measures=p.get("remedialMeasures", []),
                        liability=p.get("liability"),
                    )
                )
            contract = DC(
                info=CI(
                    contract_id=info["contractId"],
                    contract_name=info["contractName"],
                    subject_ids=info.get("subjectIds", []),
                    subject_types=info.get("subjectTypes", []),
                    signatures=info["signatures"],
                    valid_until=info.get("validUntil", ""),
                ),
                policies=policies,
            )
            errors = validate_contract(contract)
            assert errors == [], f"{path.name}: {errors}"


# ---------------------------------------------------------------------------
# Reusable conformance driver for third-party engines
# ---------------------------------------------------------------------------

def run_consistency_suite(engine: UsageControlEngine) -> None:
    """Drive any ``UsageControlEngine`` through the normative behaviour checks.

    Connector implementations can call this from their own test-suites to
    demonstrate consistency with TC609 semantics:

        engine = MyConnectorEngine()
        run_consistency_suite(engine)   # raises AssertionError on deviation
    """
    allow = make_allow_policy(
        constraints=[
            Constraint(name=ConstraintName.EXECUTION_ENV, operator=Operator.IS_A, value="data-sandbox")
        ],
        prior_obligations=[{"action": "log", "order": 1}],
    )
    contract = make_contract([allow])

    # UC 7.1.2.2: parse + integrity/validity check
    assert engine.load_contract(contract) == []

    # UC 7.1.2.3: explicit decision vocabulary
    decision, _ = engine.verify(make_context(environment="bare-metal"), "read")
    assert decision in {Decision.DENIED, Decision.DEFAULT_DENY}

    decision, _ = engine.verify(make_context(), "read")
    assert decision == Decision.CONDITIONAL  # obligations pending

    # EV Table 18 d): evidence for each stage
    stages = {e.stage for e in engine.evidence()}
    assert "strategy_parse" in stages and "behavior_verify" in stages

    # default deny semantics
    decision, _ = engine.verify(make_context(product_id="DP-OTHER"), "read")
    assert decision in {Decision.DENIED, Decision.DEFAULT_DENY}


def test_reference_engine_passes_consistency_suite():
    run_consistency_suite(ReferenceEngine())


def test_engine_protocol_is_abstract():
    with pytest.raises(TypeError):
        UsageControlEngine()  # abstract protocol cannot be instantiated
