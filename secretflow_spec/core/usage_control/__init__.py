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
"""Trusted-data-space usage-control primitives aligned with TC609 technical documents.

Public entry points::

    from secretflow_spec.core.usage_control import (
        DigitalContract, ContractPolicy, ContractObject, PolicyExecutePoint,
        Operation, Constraint, PolicyType, OperationAction, ConstraintName,
        Operator, Decision, UsageContext, EvidenceRecord,
        ReferenceEngine, UsageControlEngine,
        validate_contract, detect_policy_conflicts, verify_operation,
        check_obligation_ordering, validate_policy_inheritance,
        check_contract_id_format,
    )

See ``README.md`` in this package for the clause-level traceability matrix.
"""

from .engine import ReferenceEngine, UsageControlEngine
from .model import (
    Constraint,
    ConstraintName,
    ContractInfo,
    ContractObject,
    ContractPolicy,
    Decision,
    DigitalContract,
    EvidenceRecord,
    Operation,
    OperationAction,
    Operator,
    PolicyExecutePoint,
    PolicyType,
    UsageContext,
)
from .validator import (
    ValidationError,
    check_contract_id_format,
    check_obligation_ordering,
    detect_policy_conflicts,
    PolicyConflict,
    validate_contract,
    validate_policy,
    validate_policy_inheritance,
    verify_operation,
)

__all__ = [
    "Constraint",
    "ConstraintName",
    "ContractInfo",
    "ContractObject",
    "ContractPolicy",
    "Decision",
    "DigitalContract",
    "EvidenceRecord",
    "Operation",
    "OperationAction",
    "Operator",
    "PolicyConflict",
    "PolicyExecutePoint",
    "PolicyType",
    "ReferenceEngine",
    "UsageContext",
    "UsageControlEngine",
    "ValidationError",
    "check_contract_id_format",
    "check_obligation_ordering",
    "detect_policy_conflicts",
    "validate_contract",
    "validate_policy",
    "validate_policy_inheritance",
    "verify_operation",
]
