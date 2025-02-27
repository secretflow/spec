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
from dataclasses import dataclass
from enum import IntFlag

from secretflow_spec.core.types import StrEnum
from secretflow_spec.core.version import SPEC_VERSION
from secretflow_spec.v1.data_pb2 import (
    DistData,
    IndividualTable,
    SystemInfo,
    TableSchema,
    VerticalTable,
)

from .base import DistDataType


@enum.unique
class VTableFormat(StrEnum):
    CSV = "csv"
    ORC = "orc"


_same_type = {
    "int": "int64",
    "float": "float64",
    "int64": "int",
    "float64": "float",
}


@enum.unique
class VTableFieldType(StrEnum):
    STR = "str"
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    INT64 = "int64"
    UINT8 = "uint8"
    UINT16 = "uint16"
    UINT32 = "uint32"
    UINT64 = "uint64"
    FLOAT16 = "float16"
    FLOAT32 = "float32"
    FLOAT64 = "float64"

    def is_string(self) -> bool:
        return self.value == "str"

    def is_bool(self) -> bool:
        return self.value == "bool"

    def is_integer(self) -> bool:
        v = str(self.value)
        return v.startswith("int") or v.startswith("uint")

    def is_float(self) -> bool:
        v = str(self.value)
        return v.startswith("float")

    @staticmethod
    def is_same_type(t1: str, t2: str) -> bool:
        return t1 == t2 or (t1 in _same_type and _same_type[t1] == t2)


class VTableFieldKind(IntFlag):
    UNKNOWN = 0
    FEATURE = 1 << 0
    LABEL = 1 << 1
    ID = 1 << 2

    FEATURE_LABEL = FEATURE | LABEL
    ALL = FEATURE | LABEL | ID

    @staticmethod
    def from_str(str_value: str) -> "VTableFieldKind":
        if str_value == "UNKNOWN":
            return VTableFieldKind.UNKNOWN

        value = VTableFieldKind.UNKNOWN
        fields = str_value.split("|")
        for key in fields:
            value |= VTableFieldKind[key].value

        return VTableFieldKind(value)

    def __str__(self):
        if self.value == VTableFieldKind.UNKNOWN:
            return "UNKNOWN"

        members = [VTableFieldKind.FEATURE, VTableFieldKind.LABEL, VTableFieldKind.ID]
        fields = [m.name for m in members if self.value & m]

        return "|".join(fields)


@dataclass
class VTableField:
    name: str
    type: VTableFieldType
    kind: VTableFieldKind

    def __post_init__(self):
        self.type = VTableFieldType(self.type)


class VTableSchema:
    def __init__(self, fields: list[VTableField] | dict[str, VTableField]) -> None:
        if isinstance(fields, list):
            fields = {f.name: f for f in fields}
        self.fields: dict[str, VTableField] = fields

    def __getitem__(self, key: int | str) -> VTableField:
        return self.get_field(key)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, VTableSchema):
            return self.fields == value.fields

        return False

    def __contains__(self, keys: list[str] | str) -> bool:
        if isinstance(keys, list):
            return all(item in self.fields for item in keys)
        return keys in self.fields

    @property
    def names(self) -> list[str]:
        return [f.name for f in self.fields.values()]

    @property
    def kinds(self) -> dict[str, VTableFieldKind]:
        return {f.name: f.kind for f in self.fields.values()}

    @property
    def types(self) -> dict[str, str]:
        return {f.name: f.type for f in self.fields.values()}

    def get_field(self, key: int | str) -> VTableField:
        if isinstance(key, int):
            keys = self.fields.keys()
            key = next(iter(keys)) if key == 0 else list(keys)[key]

        return self.fields[key]

    def select(self, columns: list[str]) -> "VTableSchema":
        fields = {n: self.fields[n] for n in columns}
        return VTableSchema(fields)

    @staticmethod
    def from_dict(
        features: dict[str, str] = None,
        labels: dict[str, str] = None,
        ids: dict[str, str] = None,
    ) -> "VTableSchema":
        kinds = [VTableFieldKind.FEATURE, VTableFieldKind.LABEL, VTableFieldKind.ID]
        values = [features, labels, ids]
        fields = []
        for kind, value in zip(kinds, values):
            if not value:
                continue
            fields.extend([VTableField(name, typ, kind) for name, typ in value.items()])

        return VTableSchema(fields)

    @staticmethod
    def from_pb_str(pb_str: str) -> "VTableSchema":
        pb = TableSchema()
        pb.ParseFromString(pb_str)
        return VTableSchema.from_pb(pb)

    @staticmethod
    def from_pb(schema: TableSchema) -> "VTableSchema":
        fields: list[VTableField] = []
        kind_list = [VTableFieldKind.ID, VTableFieldKind.FEATURE, VTableFieldKind.LABEL]
        name_list = [schema.ids, schema.features, schema.labels]
        type_list = [schema.id_types, schema.feature_types, schema.label_types]
        for kind, names, types in zip(kind_list, name_list, type_list):
            res = [VTableField(n, t, kind) for n, t in zip(names, types)]
            fields.extend(res)
        return VTableSchema(fields)

    def to_pb(self) -> TableSchema:
        features, feature_types = [], []
        labels, label_types = [], []
        ids, id_types = [], []

        for f in self.fields.values():
            if f.kind == VTableFieldKind.FEATURE:
                feature_types.append(str(f.type))
                features.append(f.name)
            elif f.kind == VTableFieldKind.LABEL:
                label_types.append(str(f.type))
                labels.append(f.name)
            elif f.kind == VTableFieldKind.ID:
                id_types.append(str(f.type))
                ids.append(f.name)
            else:
                raise ValueError(f"invalid vtable field kind: {f}")

        return TableSchema(
            features=features,
            feature_types=feature_types,
            labels=labels,
            label_types=label_types,
            ids=ids,
            id_types=id_types,
        )


@dataclass
class VTableParty:
    party: str = ""
    uri: str = ""
    format: str = ""
    null_strs: list = None
    schema: VTableSchema = None

    @property
    def columns(self) -> list[str]:
        return self.schema.names

    @property
    def kinds(self) -> dict[str, VTableFieldKind]:
        return self.schema.kinds

    @property
    def types(self) -> dict[str, str]:
        return self.schema.types

    @staticmethod
    def from_dict(
        party: str = "",
        format: str = "",
        uri: str = "",
        null_strs: list = None,
        features: dict[str, str] = None,
        labels: dict[str, str] = None,
        ids: dict[str, str] = None,
    ) -> "VTableParty":
        return VTableParty(
            party=party,
            uri=uri,
            format=format,
            null_strs=null_strs,
            schema=VTableSchema.from_dict(features, labels, ids),
        )

    @staticmethod
    def from_pb(dr: DistData.DataRef, pb_schema: TableSchema) -> "VTableParty":
        return VTableParty(
            party=dr.party,
            uri=dr.uri,
            format=dr.format,
            null_strs=list(dr.null_strs),
            schema=VTableSchema.from_pb(pb_schema),
        )

    def to_pb(self) -> tuple[DistData.DataRef, TableSchema]:
        pb_dr = DistData.DataRef(
            party=self.party,
            uri=self.uri,
            format=self.format,
            null_strs=self.null_strs,
        )
        pb_schema = self.schema.to_pb()
        return pb_dr, pb_schema


class VTable:
    def __init__(
        self,
        name: str,
        parties: dict[str, VTableParty] | list[VTableParty],
        line_count: int = -1,
        system_info: SystemInfo = None,
    ):
        type = (
            DistDataType.INDIVIDUAL_TABLE
            if len(parties) == 1
            else DistDataType.VERTICAL_TABLE
        )

        if isinstance(parties, list):
            parties = {dr.party: dr for dr in parties}

        self.name = name
        self.type = str(type)
        self.parties = parties
        self.line_count = line_count
        self.system_info = system_info

    @property
    def is_individual(self) -> bool:
        return self.type == DistDataType.INDIVIDUAL_TABLE

    @property
    def columns(self) -> list[str]:
        ret = []
        for p in self.schemas.values():
            ret.extend(p.names)
        return ret

    @property
    def schemas(self) -> dict[str, VTableSchema]:
        return {name: p.schema for name, p in self.parties.items()}

    @property
    def flatten_schema(self) -> VTableSchema:
        if len(self.parties) == 1:
            return next(iter(self.parties.values())).schema
        else:
            fields = []
            for s in self.parties.values():
                fields.extend(s.schema.fields.values())
            return VTableSchema(fields)

    def get_party(self, key: str | int) -> VTableParty:
        if isinstance(key, int):
            keys = self.parties.keys()
            key = next(iter(keys)) if key == 0 else list(keys)[key]

        return self.parties[key]

    def get_schema(self, key: str | int) -> VTableSchema:
        return self.get_party(key).schema

    @staticmethod
    def from_output_uri(
        output_uri: str,
        schemas: dict[str, VTableSchema],
        line_count: int = -1,
        name: str = None,
        format: str = VTableFormat.ORC,
        null_strs: list[str] = None,
        system_info: SystemInfo = None,
    ) -> "VTable":
        assert len(schemas) > 0, f"empty schema, uri={output_uri}"
        parties = {
            name: VTableParty(
                party=name,
                uri=output_uri,
                format=str(format),
                null_strs=null_strs,
                schema=s,
            )
            for name, s in schemas.items()
        }
        return VTable(
            name=name if name else output_uri,
            parties=parties,
            line_count=line_count,
            system_info=system_info,
        )

    @staticmethod
    def from_distdata(dd: DistData, columns: list[str] = None) -> "VTable":
        dd_type = dd.type.lower()
        if dd_type not in [
            DistDataType.VERTICAL_TABLE,
            DistDataType.INDIVIDUAL_TABLE,
        ]:
            raise ValueError(f"Unsupported DistData type {dd_type}")
        # parse meta
        is_individual = dd.type == DistDataType.INDIVIDUAL_TABLE
        meta = IndividualTable() if is_individual else VerticalTable()
        dd.meta.Unpack(meta)
        pb_schemas = [meta.schema] if is_individual else meta.schemas
        if len(pb_schemas) == 0:
            raise ValueError(f"empty schema")
        if len(dd.data_refs) != len(pb_schemas):
            raise ValueError(
                f"schemas<{len(pb_schemas)}> and data_refs<{len(dd.data_refs)}> mismatch"
            )

        parties = {
            dr.party: VTableParty.from_pb(dr, ps)
            for dr, ps in zip(dd.data_refs, pb_schemas)
        }

        vtbl = VTable(
            name=dd.name,
            parties=parties,
            system_info=dd.system_info,
            line_count=meta.line_count,
        )
        if columns:
            vtbl = vtbl.select(columns)
        return vtbl

    def to_distdata(self) -> DistData:
        pb_schemas = []
        pb_data_refs = []
        for p in self.parties.values():
            pb_dr, pb_schema = p.to_pb()
            pb_data_refs.append(pb_dr)
            pb_schemas.append(pb_schema)

        if len(pb_schemas) == 1:
            meta = IndividualTable(schema=pb_schemas[0], line_count=self.line_count)
        else:
            meta = VerticalTable(schemas=pb_schemas, line_count=self.line_count)
        dd = DistData(
            version=SPEC_VERSION,
            name=self.name,
            type=self.type,
            system_info=self.system_info,
            data_refs=pb_data_refs,
        )
        if meta:
            dd.meta.Pack(meta)
        return dd

    def _copy(self, schemas: dict[str, VTableSchema]) -> "VTable":
        parties = {}
        for key, schema in schemas.items():
            p = self.parties[key]
            parties[key] = VTableParty(
                party=p.party,
                uri=p.uri,
                format=p.format,
                null_strs=p.null_strs,
                schema=schema,
            )

        return VTable(
            name=self.name,
            parties=parties,
            line_count=self.line_count,
            system_info=self.system_info,
        )

    def sort_partitions(self, orders: list[str]) -> "VTable":
        if set(orders) != set(self.parties.keys()):
            raise ValueError(f"parties mismatch, {orders}<>{self.parties.keys()}")

        parties = {}
        for key in orders:
            parties[key] = self.parties[key]

        return VTable(self.name, parties, self.line_count, self.system_info)

    def drop(self, columns: list[str]) -> "VTable":
        """
        drop some columns, return new VTable
        """
        if not columns:
            raise ValueError(f"empty exclude columns set")

        excludes_set = set(columns)
        schemas = {}
        for party, p in self.parties.items():
            if len(excludes_set) == 0:
                schemas[party] = p.schema
                break
            fields = {}
            for f in p.schema.fields.values():
                if f.name in excludes_set:
                    excludes_set.remove(f.name)
                    continue
                fields[f.name] = f
            if len(fields) == 0:
                continue
            schemas[party] = VTableSchema(fields)

        if len(excludes_set) > 0:
            raise ValueError(f"unknowns columns, {excludes_set}")

        return self._copy(schemas)

    def select(self, columns: list[str]) -> "VTable":
        """
        select and sort by column names, return new VTable
        """
        if not columns:
            raise ValueError(f"columns cannot be empty")

        seen = set()
        duplicates = set(x for x in columns if x in seen or seen.add(x))
        if duplicates:
            raise f"has duplicate items<{duplicates}> in {columns}"

        columns_map = {name: idx for idx, name in enumerate(columns)}

        schemas = {}
        for party, p in self.parties.items():
            fields = {
                name: field
                for name, field in p.schema.fields.items()
                if field.name in columns_map
            }
            if len(fields) == 0:
                continue

            # sort by keys
            fields = {n: fields[n] for n in columns_map.keys() if n in fields}

            for n in fields.keys():
                del columns_map[n]

            schemas[party] = VTableSchema(fields)
            if len(columns_map) == 0:
                continue

        if len(columns_map) > 0:
            raise ValueError(f"unknowns columns, {columns_map.keys()}")

        return self._copy(schemas)

    def select_by_kinds(self, kinds: VTableFieldKind) -> "VTable":
        if kinds == VTableFieldKind.ALL:
            return self

        schemas = {}
        for party, p in self.parties.items():
            schema = p.schema
            fields = {
                name: field
                for name, field in schema.fields.items()
                if field.kind & kinds
            }
            if len(fields) > 0:
                schemas[party] = VTableSchema(fields)

        return self._copy(schemas)

    def check_kinds(self, kinds: VTableFieldKind):
        assert kinds != 0 and kinds != VTableFieldKind.ALL
        mismatch = {}
        for p in self.parties.values():
            for f in p.schema.fields.values():
                if not (kinds & f.kind):
                    mismatch[f.name] = str(f.kind)

        if len(mismatch) > 0:
            raise ValueError(f"kind of {mismatch} mismatch, expected {kinds}")
