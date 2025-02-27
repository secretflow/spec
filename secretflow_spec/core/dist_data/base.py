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

import enum

from secretflow_spec.core.types import StrEnum


@enum.unique
class DistDataType(StrEnum):
    """
    builtin distdata type
    """

    # tables
    OUTDATED_VERTICAL_TABLE = "sf.table.vertical_table"  # deprecated
    VERTICAL_TABLE = "sf.table.vertical"
    INDIVIDUAL_TABLE = "sf.table.individual"
    # report
    REPORT = "sf.report"
    # if input of component is optional, then the corresponding type can be NULL
    NULL = "sf.null"
