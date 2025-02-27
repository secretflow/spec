# Copyright 2024 Ant Group Co., Ltd.
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

from secretflow_spec.core.component import (
    BuiltinType,
    Component,
    Input,
    Output,
    UnionGroup,
    UnionSelection,
)
from secretflow_spec.core.definition import Definition, Field, Interval
from secretflow_spec.core.discovery import load_component_modules
from secretflow_spec.core.dist_data.file import ObjectFile
from secretflow_spec.core.dist_data.report import Reporter
from secretflow_spec.core.dist_data.vtable import (
    VTable,
    VTableField,
    VTableFieldKind,
    VTableFieldType,
    VTableFormat,
    VTableParty,
    VTableSchema,
)
from secretflow_spec.core.registry import Registry, register
from secretflow_spec.core.storage import (
    LocalStorage,
    S3Storage,
    Storage,
    StorageType,
    make_storage,
)
from secretflow_spec.core.types import StrEnum, Version
from secretflow_spec.core.utils import build_node_eval_param, to_attribute, to_type
from secretflow_spec.core.version import (
    SPEC_VERSION,
    SPEC_VERSION_MAJOR,
    SPEC_VERSION_MINOR,
)

__all__ = [
    "SPEC_VERSION",
    "SPEC_VERSION_MAJOR",
    "SPEC_VERSION_MINOR",
    # component
    "BuiltinType",
    "Component",
    "Input",
    "Output",
    "UnionGroup",
    "UnionSelection",
    # definition
    "Definition",
    "Field",
    "Interval",
    # registry
    "Registry",
    "register",
    # discovery
    "load_component_modules",
    # dist_data.file
    "ObjectFile",
    # dist_data.report
    "Reporter",
    # dist_data.vtable
    "VTable",
    "VTableField",
    "VTableFieldKind",
    "VTableFieldType",
    "VTableFormat",
    "VTableParty",
    "VTableSchema",
    # storage
    "make_storage",
    "StorageType",
    "Storage",
    "S3Storage",
    "LocalStorage",
    # types
    "StrEnum",
    "Version",
    # utils
    "to_type",
    "to_attribute",
    "build_node_eval_param",
]
