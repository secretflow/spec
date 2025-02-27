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


import json
from typing import Any

from secretflow_spec.core.types import Version
from secretflow_spec.core.version import SPEC_VERSION
from secretflow_spec.v1.data_pb2 import DistData, ObjectFileInfo, SystemInfo


class ObjectFile:
    def __init__(
        self,
        name: str,
        type: str,
        data_refs: list[DistData.DataRef],
        version: Version,
        public_info: Any,
        attributes: dict[str, str] = None,
        system_info: SystemInfo = None,
    ):
        self.name = name
        self.type = type
        self.version = version
        self.public_info = public_info
        self.attributes = attributes
        self.data_refs = data_refs
        self.system_info = system_info

    @staticmethod
    def from_distdata(dd: DistData) -> "ObjectFile":
        meta = ObjectFileInfo()
        dd.meta.Unpack(meta)
        attributes = dict(meta.attributes)
        if not ("version" in attributes and "public_info" in attributes):
            raise ValueError(f"invalid FileInfo format {attributes}")
        version = Version.from_str(attributes.pop("version"))
        public_info = json.loads(attributes.pop("public_info"))

        return ObjectFile(
            name=dd.name,
            type=dd.type,
            data_refs=list(dd.data_refs),
            version=version,
            public_info=public_info,
            attributes=attributes,
            system_info=dd.system_info,
        )

    def to_distdata(self) -> "DistData":
        if self.name == "":
            raise ValueError(f"dist_data file name is empty")
        if self.type == "":
            raise ValueError(f"dist_data type is empty")

        attributes = {
            "version": str(self.version),
            "public_info": json.dumps(self.public_info),
        }
        if self.attributes:
            attributes.update(self.attributes)
        meta = ObjectFileInfo(attributes=attributes)

        dd = DistData(
            version=SPEC_VERSION,
            name=self.name,
            type=self.type,
            data_refs=self.data_refs,
            system_info=self.system_info,
        )
        dd.meta.Pack(meta)
        return dd

    def check(self, file_type: str = None, max_version: Version = None):
        if file_type and file_type != self.type:
            raise ValueError(f"type mismatch, expect {file_type} but got {self.type}")

        if max_version and not (
            max_version.major == self.version.major
            and max_version.minor >= self.version.minor
        ):
            raise ValueError(
                f"max_version mismatch, expect {max_version} but got {self.version}"
            )
