# Trusted Data Space Usage Control (TC609 aligned)

Machine-readable implementation and consistency test-suite for the usage-control
provisions of China's trusted-data-space technical documents, published by the
National Data Standardization Committee (全国数据标准化技术委员会, 全国数标委) and
CCSA TC609. All source documents are publicly downloadable from
[tc609.org.cn](https://www.tc609.org.cn) and [nda.gov.cn](https://www.nda.gov.cn).

This package turns the *normative text* of three technical documents into
executable artifacts:

| Artifact | Source |
|---|---|
| `model.py` — contract/policy data model | *Digital Contract Requirements* §6.2.1–6.2.2.4, Tables 1–7 |
| `validator.py` — structural validation, conflict detection, behaviour verification | *Digital Contract Requirements* §7.1/7.2/8; *Usage Control Requirements* §7.1.2.2–7.1.2.4 |
| `engine.py` — reference usage-control pipeline + pluggable protocol | *Usage Control Requirements* §7, §8.1 |
| `schema/digital_contract.schema.json` — JSON Schema (draft 2020-12) | idem |
| `schema/strategy_dispatch.schema.json` — `/strategySend` request body | *Usage Control Requirements* §9.2.1 Table 2 |
| `examples/scenario[1-5]*.json` | *Digital Contract Requirements* Appendix D scenarios |
| `tests/test_usage_control.py` — consistency suite | see traceability matrix below |

## Clause traceability matrix

### A. Digital Contract Requirements (DC, 征求意见稿 2025-08)

| Clause | Requirement (abridged) | Implementation | Tests |
|---|---|---|---|
| §6.1 | contract = info + ≥1 policies | `DigitalContract`, `validate_contract` | TC-DC-02 |
| §6.2.1 Table 1 | 13 contract-info items | `ContractInfo` | TC-DC-02 |
| §6.2.2 | policy triage allow/forbid/obligation + type-specific extensions | `PolicyType`, `ContractPolicy` | TC-DC-03 |
| §6.2.2.1 Table 2 | contract object fields | `ContractObject` | schema conformance |
| §6.2.2.2 Table 3 | policy execute point fields | `PolicyExecutePoint` | schema conformance |
| §6.2.2.3 Table 4 | 25 operation behaviours + custom operations | `OperationAction` | TC-DC-04 |
| §6.2.2.4 Tables 5–7 | constraint = name(17) + operator(12) + value | `Constraint`, `ConstraintName`, `Operator` | TC-DC-04 |
| §7.1 c) | core-field completeness auto-check at creation | `validate_contract` | TC-DC-02 |
| §7.2.1 | composite 47-char contract identifier | `check_contract_id_format` | TC-DC-01 |
| Appendix D | 5 application scenarios | `examples/scenario*.json` | schema + engine round-trip |

### B. Usage Control Requirements (UC)

| Clause | Requirement (abridged) | Implementation | Tests |
|---|---|---|---|
| §7.1.2.2 a–f | integrity check, syntax/semantic parse, conflict detection, executable format | `load_contract`, `detect_policy_conflicts` | TC-UC-05, EV-DC-A |
| §7.1.2.3 a | context collection | `UsageContext.get` | TC-UC-03/04 |
| §7.1.2.3 b | condition verification (12 operators) | `evaluate_constraint`, `verify_operation` | TC-UC-03/04 |
| §7.1.2.3 c | explicit decision: allowed/conditional/denied/default_denied | `Decision`, `verify_operation` | TC-UC-01/02, EV-UC-A |
| §7.1.2.4 b | conditional-allow: fulfil obligations then re-verify | `ReferenceEngine.execute` | EV-UC-C |
| §7.1.2.4 e | strict obligation ordering | `check_obligation_ordering` | TC-UC-06 |
| §7.1.2.4 i | policy inheritance for derived data | `validate_policy_inheritance` | TC-UC-07 |
| §7.1.3 / §7.2.3 | evidence records for parse/verify/execute stages | `EvidenceRecord`, `ReferenceEngine` | EV-UC-D |
| §9.2.1 Table 2 | `/strategySend` field composition (47/36/36-char ids, ISO-8601, signature) | `strategy_dispatch.schema.json`, `check_contract_id_format` | TC-UC-01/08 |

### C. Technical Capability Evaluation Specification (EV)

| Checkpoint | Requirement (abridged) | Tests |
|---|---|---|
| Table 18 a) 数据使用环境 | sandbox/controlled execution environment enforced | EV-UC-A |
| Table 18 c) 控制策略执行能力 | real-time verification + violation blocking | EV-UC-C |
| Table 18 d) 使用存证能力 | complete evidence pipeline | EV-UC-D |
| Table 19 a) 数字合约完整性保障 | tampered contracts rejected | EV-DC-A |
| Table 19 b) 数字合约真实性保障 | unsigned contracts rejected | EV-DC-A |

## Conformance testing for third-party connectors

`UsageControlEngine` is the protocol a policy-execute point must implement.
The suite in `tests/test_usage_control.py` exposes `run_consistency_suite(engine)`,
which drives any implementation through the normative behaviour checks:

```python
from secretflow_spec.core.usage_control import ReferenceEngine
from tests.test_usage_control import run_consistency_suite

run_consistency_suite(MyConnectorEngine())   # raises on any deviation
run_consistency_suite(ReferenceEngine())     # self-consistency baseline
```

## Findings fed back to the standards community

While translating the text, two observations worth raising with the draft
owners emerged (deliberately NOT "fixed" in code, only documented):

1. **Appendix D vs Table 6.1 constraint-name mismatch.** Appendix D scenario
   examples use constraint names `timeInterval`, `purpose` and `inform` that
   are absent from Table 6.1's canonical 17-name list. This package models
   them as `extend` (Table 6.1 #17, extensibility) but a future revision
   should align the appendix with Table 6.1.
2. **Table numbering drift.** The constraint-operator table is labelled
   "表 7.2" while the surrounding numbering follows Table 5/6.1 conventions —
   worth normalizing in a future revision.

## License

Apache License 2.0, consistent with the repository.
