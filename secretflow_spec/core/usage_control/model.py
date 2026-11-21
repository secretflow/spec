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
"""Digital contract and usage-control data model.

Structurally aligned with the following public technical documents of the
Chinese National Data Standardization Committee (全国数据标准化技术委员会)
and CCSA TC609:

- ``TC609-6-2025-01`` Trusted Data Space - Technical Architecture
- Technical document ``Trusted Data Space - Digital Contract - Technical
  Requirements`` (draft for comments, 2025-08), Sections 6.2.1-6.2.2 and
  Tables 1-7 / Appendix D.
- Technical document ``Trusted Data Space - Usage Control - Technical
  Requirements``, Sections 7.1-7.2 and Tables 1-4.

Every data class and enum carries a ``ref`` marker (kept in docstrings and the
``CLAUSE_REF`` mapping in ``validator.py``) so that consistency tests can be
traced back to individual clauses.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class PolicyType(enum.Enum):
    """Contract policy category (Digital Contract Requirements, 6.2.2).

    - ALLOW: permits a subject to perform an operation on the object; the
      extension carries *prior obligations* that must be fulfilled first.
    - FORBID: denies an operation; the extension carries *remedial measures*
      triggered when the forbidden behaviour occurs.
    - OBLIGATION: requires the subject to perform a specific operation; the
      extension carries *liability* applied when the obligation is breached.
    """

    ALLOW = "allow"
    FORBID = "forbid"
    OBLIGATION = "obligation"


class OperationAction(enum.Enum):
    """Operation behaviour enumerated in Digital Contract Requirements Table 4.

    25 canonical operations plus ``EXTEND`` for custom operations (Table 4
    item 25 explicitly allows customised operations).
    """

    CONVERT = "convert"  # 1 转换
    ANONYMIZE = "anonymize"  # 2 匿名化
    MASK = "mask"  # 3 脱敏
    BLUR = "blur"  # 4 模糊化
    ACCESS = "access"  # 5 访问
    READ = "read"  # 6 读取
    COPY = "copy"  # 7 复制
    STORE = "store"  # 8 存储
    DOWNLOAD = "download"  # 9 下载
    PROCESS = "process"  # 10 加工
    JOINT_DEVELOP = "jointDevelop"  # 11 联合开发
    CACHE = "cache"  # 12 缓存
    BURN_AFTER_USE = "burnAfterUse"  # 13 用后即焚
    DISTRIBUTE = "distribute"  # 14 分发
    EXPORT = "export"  # 15 导出
    AUTHORIZE_USE = "authorizeUse"  # 16 授权使用
    DELIVER = "deliver"  # 17 交付
    SELL = "sell"  # 18 交易
    ACCEPT_TRACKING = "acceptTracking"  # 19 接受追踪
    LOG = "log"  # 20 日志记录
    DELETE = "delete"  # 21 删除
    INFORM = "inform"  # 22 通知
    ALERT = "alert"  # 23 异常提醒
    COMPENSATE = "compensate"  # 24 赔偿
    EXTEND = "extend"  # 25 扩展操作


class ConstraintName(enum.Enum):
    """Constraint names from Digital Contract Requirements Table 6.1 (17 items).

    Values follow the English names used by the Appendix D scenario examples
    (e.g. ``executionEnv``, ``encryptMode``, ``payAmount``).
    """

    TIME = "time"  # 1 时间 (ISO-8601 time point)
    TIME_WINDOW = "timeWindow"  # 2 时间窗口 (ISO-8601 duration / range)
    NETWORK_ADDRESS = "networkAddress"  # 3 网络地址
    PHYSICAL_ADDRESS = "physicalAddress"  # 4 物理地址
    SECURITY_LEVEL = "securityLevel"  # 5 安全等级
    COUNT = "count"  # 6 次数 (positive integer)
    DATA_SIZE = "dataSize"  # 7 数据规模 (bytes, positive integer)
    DATA_RECORD_NUMBER = "dataRecordNumber"  # 8 数据记录数 (positive integer)
    DATA_FIELD = "dataField"  # 9 数据字段 (multiple supported)
    DATA_FIELD_VALUE = "dataFieldValue"  # 10 数据字段值
    FUNCTION = "function"  # 11 函数
    EXECUTION_ENV = "executionEnv"  # 12 执行环境
    ENCRYPT_MODE = "encryptMode"  # 13 加密方式
    DELIVERY_METHOD = "deliveryMethod"  # 14 交付方式
    DELIVERY_CHANNEL = "deliveryChannel"  # 15 交付渠道
    PAY_AMOUNT = "payAmount"  # 16 交易金额
    EXTEND = "extend"  # 17 扩展信息


class Operator(enum.Enum):
    """Constraint operators from Digital Contract Requirements Table 7.2 (12 items)."""

    EQ = "eq"  # 1 等于
    GT = "gt"  # 2 大于
    GTEQ = "gteq"  # 3 大于或等于
    HAS_PART = "hasPart"  # 4 包含部分
    IS_A = "isA"  # 5 属于实例
    IS_ALL_OF = "isAllOf"  # 6 全部属于
    IS_ANY_OF = "isAnyOf"  # 7 任意属于
    IS_NONE_OF = "isNoneOf"  # 8 不属于
    IS_PART_OF = "isPartOf"  # 9 属于部分
    LT = "lt"  # 10 小于
    LTEQ = "lteq"  # 11 小于或等于
    NEQ = "neq"  # 12 不等于


class Decision(enum.Enum):
    """Behaviour-verification decision results.

    Usage Control Requirements 7.1.2.3 c) requires an explicit decision among
    "允许 / 有条件允许 / 拒绝 / 默认拒绝".
    """

    ALLOWED = "allowed"
    CONDITIONAL = "conditional"
    DENIED = "denied"
    DEFAULT_DENY = "default_denied"


@dataclass
class Constraint:
    """A structured constraint (Digital Contract Requirements Table 5)."""

    name: ConstraintName
    operator: Operator
    value: Any
    ref: Optional[str] = None  # clause reference, e.g. "6.2.2.4/表6.1#12"


@dataclass
class Operation:
    """An operation behaviour on the contract object (Table 4)."""

    action: OperationAction
    constraints: List[Constraint] = field(default_factory=list)
    ref: Optional[str] = None


@dataclass
class ContractObject:
    """The contract object ("数据产品") per Digital Contract Requirements 6.2.2.1 / Table 2."""

    product_id: str
    product_name: str
    description: str = ""
    owner_id: str = ""
    expansion_item: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyExecutePoint:
    """Policy execute point info per Digital Contract Requirements 6.2.2.2 / Table 3.

    ``policy_execute_point`` identifiers are connector or business-node IDs
    (Usage Control Requirements 3.9: 策略执行节点一般是接入连接器或业务节点).
    """

    provider_pep_id: str
    provider_pep_name: str = ""
    consumer_pep_id: str = ""
    consumer_pep_name: str = ""
    expansion_item: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractPolicy:
    """One contract policy instance (Digital Contract Requirements 6.2.2).

    A policy binds objects + execute points + operations + constraints. The
    type-specific extension follows 6.2.2: allow -> prior obligation,
    forbid -> remedial measure, obligation -> liability.

    ``strategy_id`` / ``strategy_version`` correspond to the fields required
    by the platform strategy-dispatch interface (Usage Control Requirements
    Table 2, 9.2.1).
    """

    policy_type: PolicyType
    strategy_id: str
    strategy_version: str = "v1"
    objects: List[ContractObject] = field(default_factory=list)
    execute_points: List[PolicyExecutePoint] = field(default_factory=list)
    operations: List[Operation] = field(default_factory=list)
    subjects: List[str] = field(default_factory=list)
    # type-specific extension
    prior_obligations: List[Operation] = field(default_factory=list)  # allow
    remedial_measures: List[Operation] = field(default_factory=list)  # forbid
    liability: Optional[Dict[str, Any]] = None  # obligation
    expansion_item: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractInfo:
    """Contract information per Digital Contract Requirements 6.2.1 / Table 1 (13 items).

    ``contract_id`` is the 47-character unique identifier specified by
    Usage Control Requirements Table 2 (composition: 1 type code + 1 business
    node type code + 18 subject code + 4 region/industry code + 14 time code
    + 8 random code + 1 check code).
    """

    contract_id: str
    contract_name: str
    description: str = ""
    status: str = "initiated"
    created_at: str = ""
    signing_mode: str = "p2p"
    subject_ids: List[str] = field(default_factory=list)
    subject_names: List[str] = field(default_factory=list)
    subject_types: List[str] = field(default_factory=list)
    signed_at: str = ""
    signatures: Dict[str, str] = field(default_factory=dict)  # subject_id -> signature
    valid_until: str = ""
    expansion_item: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DigitalContract:
    """Digital contract = contract info + one or more contract policies (Section 6.1)."""

    info: ContractInfo
    policies: List[ContractPolicy] = field(default_factory=list)


@dataclass
class UsageContext:
    """Runtime context collected for behaviour verification (Usage Control 7.1.2.3 a)."""

    subject_id: str
    product_id: str
    connector_id: str
    application_id: str = ""
    operation: str = ""
    request_time: str = ""
    location: str = ""
    environment: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)

    def get(self, name: str) -> Any:
        """Resolve a constraint name against the context.

        Canonical names map to dedicated fields; other names fall back to
        ``attributes`` (supports custom constraints such as ``extend``).
        """
        mapping = {
            ConstraintName.TIME.value: self.request_time,
            ConstraintName.NETWORK_ADDRESS.value: self.location,
            ConstraintName.EXECUTION_ENV.value: self.environment,
            "subject": self.subject_id,
            "connector": self.connector_id,
            "application": self.application_id,
            "operation": self.operation,
        }
        if name in mapping:
            return mapping[name]
        return self.attributes.get(name)


@dataclass
class EvidenceRecord:
    """Usage evidence record (Usage Control 7.1.3 a/b, 7.2.3 b).

    Records one stage of the pipeline: ``strategy_parse``, ``behavior_verify``
    or ``operation_execute``; later submitted to the trusted data space
    service platform via the evidence-reporting channel (7.1.3 d).
    """

    stage: str
    timestamp: str
    subject: str
    object_ref: str  # e.g. product id or strategy id
    result: str
    details: Dict[str, Any] = field(default_factory=dict)
