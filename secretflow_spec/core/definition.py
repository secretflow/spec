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

import re
from dataclasses import MISSING
from dataclasses import Field as DField
from dataclasses import dataclass, field, is_dataclass
from enum import Enum, auto
from typing import Any, Type, get_args, get_origin

from google.protobuf import json_format
from google.protobuf.message import Message

from secretflow_spec.core.component import (
    Component,
    Input,
    Output,
    UnionGroup,
    UnionSelection,
)
from secretflow_spec.core.dist_data.base import DistDataType
from secretflow_spec.core.utils import clean_text
from secretflow_spec.v1.component_pb2 import (
    Attribute,
    AttributeDef,
    AttrType,
    ComponentDef,
    IoDef,
)
from secretflow_spec.v1.data_pb2 import DistData
from secretflow_spec.v1.evaluation_pb2 import NodeEvalParam

LABEL_LEN_MAX = 64


class Interval:
    def __init__(
        self,
        lower: float | int = None,
        upper: float | int = None,
        lower_closed: bool = False,
        upper_closed: bool = False,
    ):
        if lower is not None and upper is not None:
            assert upper >= lower

        self.lower = lower
        self.upper = upper
        self.lower_closed = lower_closed
        self.upper_closed = upper_closed

    @staticmethod
    def open(lower: float | int | None, upper: float | int | None) -> "Interval":
        """return (lower, upper)"""
        return Interval(
            lower=lower, upper=upper, lower_closed=False, upper_closed=False
        )

    @staticmethod
    def closed(lower: float | int | None, upper: float | int | None) -> "Interval":
        """return [lower, upper]"""
        return Interval(lower=lower, upper=upper, lower_closed=True, upper_closed=True)

    @staticmethod
    def open_closed(lower: float | int | None, upper: float | int | None) -> "Interval":
        """return (lower, upper]"""
        return Interval(lower=lower, upper=upper, lower_closed=False, upper_closed=True)

    @staticmethod
    def closed_open(lower: float | int | None, upper: float | int | None) -> "Interval":
        """return [lower, upper)"""
        return Interval(lower=lower, upper=upper, lower_closed=True, upper_closed=False)

    def astype(self, typ: type):
        assert typ in [float, int]
        if self.lower is not None:
            self.lower = typ(self.lower)
        if self.upper is not None:
            self.upper = typ(self.upper)

    def enforce_closed(self):
        if self.lower != None:
            if isinstance(self.lower, float) and not self.lower.is_integer():
                raise ValueError(f"Lower bound must be an integer, {self.lower}")
            self.lower = int(self.lower)
            if not self.lower_closed:
                self.lower += 1
                self.lower_closed = True

        if self.upper != None:
            if isinstance(self.upper, float) and not self.upper.is_integer():
                raise ValueError(f"Upper bound must be an integer, {self.upper}")
            self.upper = int(self.upper)
            if not self.upper_closed:
                self.upper -= 1
                self.upper_closed = True

    def check(self, v: float | int) -> tuple[bool, str]:
        if self.upper is not None:
            if self.upper_closed:
                if v > self.upper:
                    return (
                        False,
                        f"should be less than or equal {self.upper}, but got {v}",
                    )
            else:
                if v >= self.upper:
                    return (
                        False,
                        f"should be less than {self.upper}, but got {v}",
                    )
        if self.lower is not None:
            if self.lower_closed:
                if v < self.lower:
                    return (
                        False,
                        f"should be greater than or equal {self.lower}, but got {v}",
                    )
            else:
                if v <= self.lower:
                    return (
                        False,
                        f"should be greater than {self.lower}, but got {v}",
                    )
        return True, ""


class FieldKind(Enum):
    BasicAttr = auto()
    PartyAttr = auto()
    CustomAttr = auto()
    StructAttr = auto()
    UnionAttr = auto()
    SelectionAttr = auto()
    TableColumnAttr = auto()
    Input = auto()
    Output = auto()


def is_deprecated_field(minor_max: int) -> bool:
    return minor_max != -1


def is_deprecated_minor(minor_max: int, minor: int) -> bool:
    return minor_max != -1 and minor > minor_max


@dataclass
class _Metadata:
    prefixes: list = None
    fullname: str = ""
    name: str = ""
    type: Type = None
    kind: FieldKind = None
    desc: str = None
    is_optional: bool = False
    choices: list = None
    bound_limit: Interval = None
    list_limit: Interval = None
    default: Any = None
    selections: dict[str, UnionSelection] = None  # only used in union_group
    input_name: str = None  # only used in table_column_attr
    is_checkpoint: bool = False  # if true it will be save when dump checkpoint
    types: list[str] = None  # only used in input/output
    minor_min: int = 0  # it's supported only if minor >= minor_min
    minor_max: int = -1  # it's deprecated if minor > minor_max and minor_max != -1


class Field:
    @staticmethod
    def _field(
        kind: FieldKind,
        minor_min: int,
        minor_max: int,
        desc: str,
        md: _Metadata | None = None,
        default: Any = None,
        init=True,
    ):
        assert minor_max is not None
        if minor_max != -1 and minor_min > minor_max:
            raise ValueError(f"invalid minor version, {minor_min}, {minor_max}")
        if md is None:
            md = _Metadata()
        md.kind = kind
        md.desc = clean_text(desc)
        md.minor_min = minor_min
        md.minor_max = minor_max

        if isinstance(default, list):
            default = MISSING
            default_factory = lambda: default
        else:
            default_factory = MISSING
        return field(
            default=default,
            default_factory=default_factory,
            init=init,
            kw_only=True,
            metadata={"md": md},
        )

    @staticmethod
    def attr(
        desc: str = "",
        is_optional: bool | None = None,
        default: Any | None = None,
        choices: list | None = None,
        bound_limit: Interval | None = None,
        list_limit: Interval | None = None,
        is_checkpoint: bool = False,
        minor_min: int = 0,
        minor_max: int = -1,
    ):
        if is_optional is None:
            is_optional = default != MISSING and default is not None

        md = _Metadata(
            is_optional=is_optional,
            choices=choices,
            bound_limit=bound_limit,
            list_limit=list_limit,
            is_checkpoint=is_checkpoint,
            default=default if default != MISSING else None,
        )
        return Field._field(
            FieldKind.BasicAttr, minor_min, minor_max, desc, md, default
        )

    @staticmethod
    def party_attr(
        desc: str = "",
        list_limit: Interval | None = None,
        minor_min: int = 0,
        minor_max: int = -1,
    ):
        md = _Metadata(list_limit=list_limit)
        return Field._field(FieldKind.PartyAttr, minor_min, minor_max, desc, md)

    @staticmethod
    def struct_attr(desc: str = "", minor_min: int = 0, minor_max: int = -1):
        return Field._field(FieldKind.StructAttr, minor_min, minor_max, desc)

    @staticmethod
    def union_attr(
        desc: str = "",
        default: str = "",
        selections: list[UnionSelection] | None = None,  # only used when type is str
        minor_min: int = 0,
        minor_max: int = -1,
    ):
        if selections:
            selections = {s.name: s for s in selections}
        md = _Metadata(default=default, selections=selections)
        return Field._field(FieldKind.UnionAttr, minor_min, minor_max, desc, md)

    @staticmethod
    def selection_attr(desc: str = "", minor_min: int = 0, minor_max: int = -1):
        return Field._field(FieldKind.SelectionAttr, minor_min, minor_max, desc)

    @staticmethod
    def custom_attr(desc: str = "", minor_min: int = 0, minor_max: int = -1):
        return Field._field(FieldKind.CustomAttr, minor_min, minor_max, desc)

    @staticmethod
    def table_column_attr(
        input_name: str,
        desc: str = "",
        limit: Interval | None = None,
        is_checkpoint: bool = False,
        minor_min: int = 0,
        minor_max: int = -1,
    ):
        if input_name == "":
            raise ValueError("input_name cannot be empty")
        md = _Metadata(
            input_name=input_name,
            list_limit=limit,
            is_checkpoint=is_checkpoint,
        )
        return Field._field(FieldKind.TableColumnAttr, minor_min, minor_max, desc, md)

    @staticmethod
    def input(
        desc: str = "",
        types: list[str] = [],
        is_checkpoint: bool = False,
        list_limit: Interval = None,
        minor_min: int = 0,
        minor_max: int = -1,
    ):
        """
        the last input can be variable and the type must be list[Input]
        """
        if not types:
            raise ValueError("input types is none")
        types = [str(s) for s in types]
        md = _Metadata(types=types, is_checkpoint=is_checkpoint, list_limit=list_limit)
        return Field._field(FieldKind.Input, minor_min, minor_max, desc, md)

    @staticmethod
    def output(
        desc: str = "",
        types: list[str] = [],
        minor_min: int = 0,
        minor_max: int = -1,
    ):
        if not types:
            raise ValueError("output types is none")
        types = [str(s) for s in types]
        md = _Metadata(types=types)
        return Field._field(FieldKind.Output, minor_min, minor_max, desc, md)


class Creator:
    def __init__(self, check_exist: bool) -> None:
        self._check_exist = check_exist

    def make(self, cls: Type, kwargs: dict, minor: int):
        args = {}
        for name, field in cls.__dataclass_fields__.items():
            if name == MINOR_NAME:
                continue
            args[name] = self._make_field(field, kwargs, minor)
        if len(kwargs) > 0:
            unused = {k: self._check_unused_type(cls, k, minor) for k in kwargs.keys()}
            raise ValueError(f"unused fields {unused}")

        args[MINOR_NAME] = minor
        ins = cls(**args)
        setattr(ins, MINOR_NAME, minor)
        return ins

    def _check_unused_type(self, cls: Type, key: str, minor: int) -> str:
        UNKNOWN = "unknown"
        DEPRECATED = "deprecated"

        tokens = key.split("/")
        cur_cls = cls
        for token in tokens:
            if not is_dataclass(cur_cls):
                return UNKNOWN
            if token not in cur_cls.__dataclass_fields__:
                return UNKNOWN

            field = cur_cls.__dataclass_fields__[token]
            md: _Metadata = field.metadata["md"]
            if is_deprecated_minor(md.minor_max, minor):
                return DEPRECATED
            cur_cls = md.type
        return UNKNOWN

    def _make_field(self, field: DField, kwargs: dict, minor: int):
        md: _Metadata = field.metadata["md"]
        if is_deprecated_minor(md.minor_max, minor):
            return None

        if md.kind == FieldKind.StructAttr:
            return self._make_struct(md, kwargs, minor)
        elif md.kind == FieldKind.UnionAttr:
            return self._make_union(md, kwargs, minor)

        if minor < md.minor_min:
            return md.default

        if md.fullname not in kwargs:
            if self._check_exist and not md.is_optional:
                raise ValueError(f"{md.fullname} is required")
            else:
                return md.default

        value = kwargs.pop(md.fullname, md.default)

        if md.kind == FieldKind.Input:
            if not isinstance(value, (DistData, list)):
                raise ValueError(f"type of {md.name} should be DistData")

            return (
                value
                if isinstance(value, list) or value.type != DistDataType.NULL
                else None
            )
        elif md.kind == FieldKind.Output:
            if not isinstance(value, (Output, str)):
                raise ValueError(
                    f"type of {md.name} should be str or Output, but got {type(value)}"
                )
            return value if isinstance(value, Output) else Output(uri=value, data=None)
        elif md.kind == FieldKind.TableColumnAttr:
            return self._make_str_or_list(md, value)
        elif md.kind == FieldKind.PartyAttr:
            return self._make_str_or_list(md, value)
        elif md.kind == FieldKind.CustomAttr:
            pb_inst = md.type()
            return json_format.Parse(value, pb_inst)
        elif md.kind == FieldKind.BasicAttr:
            return self._make_basic(md, value)
        else:
            raise ValueError(f"invalid field kind, {md.fullname}, {md.kind}")

    def _make_struct(self, md: _Metadata, kwargs: dict, minor: int):
        cls = md.type
        args = {}
        for name, field in cls.__dataclass_fields__.items():
            args[name] = self._make_field(field, kwargs, minor)

        return cls(**args)

    def _make_union(self, md: _Metadata, kwargs: dict, minor: int):
        union_type = md.type
        if minor < md.minor_min:
            selected_key = md.default
        else:
            selected_key = kwargs.pop(md.fullname, md.default)

        if not isinstance(selected_key, str):
            raise ValueError(
                f"{md.fullname} should be a str, but got {type(selected_key)}"
            )
        if union_type == str:
            if selected_key not in md.selections:
                raise ValueError(f"{selected_key} not in {md.selections.keys()}")
            selection = md.selections[selected_key]
            if is_deprecated_minor(selection.minor_max, minor):
                raise ValueError(f"{selected_key} is deprecated")
            return selected_key

        choices = union_type.__dataclass_fields__.keys()
        if selected_key not in choices:
            raise ValueError(f"{selected_key} should be one of {choices}")

        selected_field = md.type.__dataclass_fields__[selected_key]
        selected_md: _Metadata = selected_field.metadata["md"]
        if is_deprecated_minor(selected_md.minor_max, minor):
            raise ValueError(f"{selected_key} is deprecated")

        args = {}
        if selected_md.kind != FieldKind.SelectionAttr:
            value = self._make_field(selected_field, kwargs, minor)
            args = {selected_key: value}
        res: UnionGroup = md.type(**args)
        res.set_selected(selected_key)
        return res

    def _make_basic(self, md: _Metadata, value):
        is_list = isinstance(value, list)
        if is_list and md.list_limit:
            is_valid, err_str = md.list_limit.check(len(value))
            if not is_valid:
                raise ValueError(f"length of {md.fullname} is valid, {err_str}")

        check_list = value if is_list else [value]
        if md.bound_limit is not None:
            for v in check_list:
                is_valid, err_str = md.bound_limit.check(v)
                if not is_valid:
                    raise ValueError(f"value of {md.fullname} is valid, {err_str}")
        if md.choices is not None:
            for v in check_list:
                if v not in md.choices:
                    raise ValueError(
                        f"value {v} must be in {md.choices}, name is {md.fullname}"
                    )
        return value

    def _make_str_or_list(self, md: _Metadata, value):
        if value is None:
            raise ValueError(f"{md.name} can not be none")
        is_list = get_origin(md.type) is list
        if not is_list:
            if isinstance(value, list):
                if len(value) != 1:
                    raise ValueError(f"{md.name} can only have one element")
                value = value[0]
            assert isinstance(
                value, str
            ), f"{md.name} must be str, but got {type(value)}"
            return value
        else:
            assert isinstance(
                value, list
            ), f"{md.name} must be list[str], but got {type(value)}"
            if md.list_limit is not None:
                is_valid, err_str = md.list_limit.check(len(value))
                if not is_valid:
                    raise ValueError(f"length of {md.name} is invalid, {err_str}")

            return value


MINOR_NAME = "_minor"
RESERVED = ["input", "output"]


class Reflector:
    def __init__(self, cls, name: str, minor: int):
        self._cls = cls
        self._name = name
        self._minor = minor
        self._inputs: list[IoDef] = []
        self._outputs: list[IoDef] = []
        self._attrs: list[AttributeDef] = []
        self._attr_types: dict[str, AttrType] = {}

    def get_inputs(self) -> list[IoDef]:
        return self._inputs

    def get_outputs(self) -> list[IoDef]:
        return self._outputs

    def get_attrs(self) -> list[AttributeDef]:
        return self._attrs

    def get_attr_types(self) -> dict[str, AttrType]:
        return self._attr_types

    def reflect(self):
        """
        Reflect dataclass to ComponentDef.
        """
        self._force_dataclass(self._cls)

        attrs: list[_Metadata] = []
        for field in self._cls.__dataclass_fields__.values():
            if field.name == MINOR_NAME:
                continue
            md = self._build_metadata(field, [])
            if md.kind == FieldKind.Input:
                is_list, prim_type = self._check_list(md.type)
                if prim_type != Input:
                    raise ValueError("input type must be Input")
                if is_list and DistDataType.NULL in md.types:
                    raise ValueError("input type cannot be null if is variable")
                io_def = self._reflect_io(md, is_list)
                self._inputs.append(io_def)
            elif md.kind == FieldKind.Output:
                if md.type != Output:
                    raise ValueError("output type must be Output")
                io_def = self._reflect_io(md)
                self._outputs.append(io_def)
            else:
                attrs.append(md)

        for md in attrs:
            self._reflect_attr(md)

        # check input variable
        for idx, io in enumerate(self._inputs):
            if is_deprecated_field(io.minor_max):
                continue
            if io.is_variable and idx != len(self._inputs) - 1:
                raise ValueError(f"variable input must be the last one")

    def _reflect_io(self, md: _Metadata, is_list: bool = False):
        assert (
            DistDataType.OUTDATED_VERTICAL_TABLE not in md.types
        ), f"sf.table.vertical_table is deprecated, please use sf.table.vertical in {md.fullname}"
        variable_min, variable_max = 0, -1
        if is_list and md.list_limit:
            l = md.list_limit
            l.enforce_closed()
            variable_min = l.lower if l.lower else 0
            variable_max = l.upper if l.upper else -1

        is_optional = DistDataType.NULL in md.types
        return IoDef(
            name=md.name,
            desc=md.desc,
            types=md.types,
            is_optional=is_optional,
            is_variable=is_list,
            variable_min=variable_min,
            variable_max=variable_max,
            minor_min=md.minor_min,
            minor_max=md.minor_max,
        )

    def _reflect_party_attr(self, md: _Metadata):
        is_list, org_type = self._check_list(md.type)
        if org_type != str:
            raise ValueError(f"the type of party attr should be str or list[str]")
        list_min_length_inclusive, list_max_length_inclusive = self._build_list_limit(
            is_list, md.list_limit
        )
        if list_min_length_inclusive <= 0:
            md.is_optional = True
        atomic = AttributeDef.AtomicAttrDesc(
            list_min_length_inclusive=list_min_length_inclusive,
            list_max_length_inclusive=list_max_length_inclusive,
        )
        self._append_attr(AttrType.AT_PARTY, md, atomic=atomic)

    def _reflect_table_column_attr(self, md: _Metadata):
        is_list, prim_type = self._check_list(md.type)
        if prim_type != str:
            raise ValueError(
                f"input_table_attr's type must be str or list[str], but got {md.type}]"
            )

        input_name = md.input_name
        io_def = next((io for io in self._inputs if io.name == input_name), None)
        if io_def is None:
            raise ValueError(f"cannot find input io, {input_name}")

        if not input_name:
            raise ValueError(f"input_name cannot be empty in field<{md.fullname}>")

        for t in io_def.types:
            if t not in [
                str(DistDataType.VERTICAL_TABLE),
                str(DistDataType.INDIVIDUAL_TABLE),
            ]:
                raise ValueError(f"{input_name} is not defined correctly in input.")

        col_min_cnt_inclusive, col_max_cnt_inclusive = self._build_list_limit(
            is_list, md.list_limit
        )
        if col_min_cnt_inclusive <= 0:
            md.is_optional = True
        if md.prefixes:
            atomic = AttributeDef.AtomicAttrDesc(
                list_min_length_inclusive=col_min_cnt_inclusive,
                list_max_length_inclusive=col_max_cnt_inclusive,
            )
            self._append_attr(
                AttrType.AT_COL_PARAMS,
                md,
                atomic=atomic,
                col_params_binded_table=md.input_name,
            )
        else:
            if col_max_cnt_inclusive < 0:
                col_max_cnt_inclusive = 0
            preifx = md.input_name + "_"
            if md.name.startswith(preifx):
                name = md.name[len(preifx) :]
            else:
                name = md.name
            tbl_attr = IoDef.TableAttrDef(
                name=name,
                desc=md.desc,
                col_min_cnt_inclusive=col_min_cnt_inclusive,
                col_max_cnt_inclusive=col_max_cnt_inclusive,
            )
            io_def.attrs.append(tbl_attr)
            self._attr_types[md.fullname] = AttrType.AT_STRINGS

    def _reflect_attr(self, md: _Metadata):
        if md.kind == FieldKind.StructAttr:
            self._reflect_struct_attr(md)
        elif md.kind == FieldKind.UnionAttr:
            self._reflect_union_attr(md)
        elif md.kind == FieldKind.BasicAttr:
            self._reflect_basic_attr(md)
        elif md.kind == FieldKind.CustomAttr:
            self._reflect_custom_attr(md)
        elif md.kind == FieldKind.TableColumnAttr:
            self._reflect_table_column_attr(md)
        elif md.kind == FieldKind.PartyAttr:
            self._reflect_party_attr(md)
        else:
            raise ValueError(f"{md.kind} not supported, metadata={md}.")

    def _reflect_struct_attr(self, md: _Metadata):
        self._force_dataclass(md.type)

        self._append_attr(AttrType.AT_STRUCT_GROUP, md)

        prefixes = md.prefixes + [md.name]
        for field in md.type.__dataclass_fields__.values():
            sub_md = self._build_metadata(field, prefixes, md)
            self._reflect_attr(sub_md)

    def _reflect_union_attr(self, md: _Metadata):
        sub_mds = []
        prefixes = md.prefixes + [md.name]

        if md.type == str:
            if not md.selections:
                raise ValueError(f"no selections in {md.name}")
            prefix = "/".join(prefixes)
            for s in md.selections.values():
                fullname = f"{prefix}/{s.name}"
                sub_md: _Metadata = _Metadata(
                    kind=FieldKind.SelectionAttr,
                    type=str,
                    prefixes=prefixes,
                    fullname=fullname,
                    name=s.name,
                    desc=clean_text(s.desc),
                    minor_min=s.minor_min,
                    minor_max=s.minor_max,
                )
                sub_mds.append(sub_md)
        else:
            if md.selections:
                raise ValueError(
                    f"cannot assign selections when type is not str, {md.name}"
                )
            if not issubclass(md.type, UnionGroup):
                raise ValueError(
                    f"type<{md.type}> of {md.name} must be subclass of UnionGroup."
                )

            self._force_dataclass(md.type)

            for field in md.type.__dataclass_fields__.values():
                sub_md: _Metadata = self._build_metadata(field, prefixes, parent=md)
                sub_mds.append(sub_md)

        md.choices = []
        for sub_md in sub_mds:
            if not is_deprecated_field(sub_md.minor_max):
                md.choices.append(sub_md.name)

        if len(md.choices) == 0:
            raise ValueError(f"union {md.name} must have at least one choice.")

        if md.default == "":
            md.default = md.choices[0]
        elif md.default not in md.choices:
            raise ValueError(
                f"{md.default} not in {md.choices}, union name is {md.name}"
            )

        union_desc = AttributeDef.UnionAttrGroupDesc(default_selection=md.default)
        self._append_attr(AttrType.AT_UNION_GROUP, md, union=union_desc)

        for sub_md in sub_mds:
            if sub_md.kind == FieldKind.SelectionAttr:
                self._append_attr(AttrType.ATTR_TYPE_UNSPECIFIED, sub_md)
            else:
                self._reflect_attr(sub_md)

    def _reflect_custom_attr(self, md: _Metadata):
        pb_cls = md.type
        assert issubclass(pb_cls, Message), f"support protobuf class only, got {pb_cls}"
        extend_path = "secretflow.spec.extend."
        module = pb_cls.__module__
        if module.startswith(extend_path):
            module = module[len(extend_path) :]
        pb_cls_name = f"{module}.{pb_cls.__qualname__}"
        self._append_attr(AttrType.AT_CUSTOM_PROTOBUF, md, pb_cls=pb_cls_name)

    def _reflect_basic_attr(self, md: _Metadata):
        is_list, prim_type = self._check_list(md.type)
        attr_type = self._to_attr_type(prim_type, is_list)
        if attr_type == AttrType.ATTR_TYPE_UNSPECIFIED:
            raise ValueError(f"invalid primative type {prim_type}, name is {md.name}.")

        if is_list:
            list_min_length_inclusive, list_max_length_inclusive = (
                self._build_list_limit(True, md.list_limit)
            )
        else:
            list_min_length_inclusive, list_max_length_inclusive = None, None

        # check bound
        lower_bound_enabled = False
        lower_bound_inclusive = False
        lower_bound = None
        upper_bound_enabled = False
        upper_bound_inclusive = False
        upper_bound = None

        if md.bound_limit is not None:
            if prim_type not in [int, float]:
                raise ValueError(
                    f"bound limit is not supported for {prim_type}, name is {md.name}."
                )
            md.bound_limit.astype(prim_type)
            if md.choices is not None:
                for v in md.choices:
                    is_valid, err_str = md.bound_limit.check(v)
                    if not is_valid:
                        raise ValueError(
                            f"choices of {md.fullname} is valid, {err_str}"
                        )
            if md.bound_limit.lower is not None:
                lower_bound_enabled = True
                lower_bound_inclusive = md.bound_limit.lower_closed
                lower_bound = self._to_attr(prim_type(md.bound_limit.lower))
            if md.bound_limit.upper is not None:
                upper_bound_enabled = True
                upper_bound_inclusive = md.bound_limit.upper_closed
                upper_bound = self._to_attr(prim_type(md.bound_limit.upper))

        default_value = None
        allowed_values = None
        if md.is_optional and md.default is None:
            raise ValueError(f"no default value for optional field, {md.name}")
        if md.default is not None:
            if is_list and not isinstance(md.default, list):
                raise ValueError("Default value for list must be a list")

            # make sure the default type is correct
            if not isinstance(md.default, list):
                md.default = md.type(md.default)
            else:
                for idx, v in enumerate(md.default):
                    md.default[idx] = prim_type(md.default[idx])
            if md.choices is not None:
                values = md.default if is_list else [md.default]
                for v in values:
                    if v not in md.choices:
                        raise ValueError(
                            f"Default value for {v} must be one of {md.choices}"
                        )
            default_value = self._to_attr(md.default, prim_type)

        if md.choices is not None:
            allowed_values = self._to_attr(md.choices, prim_type)

        atomic = AttributeDef.AtomicAttrDesc(
            default_value=default_value,
            allowed_values=allowed_values,
            is_optional=md.is_optional,
            list_min_length_inclusive=list_min_length_inclusive,
            list_max_length_inclusive=list_max_length_inclusive,
            lower_bound_enabled=lower_bound_enabled,
            lower_bound_inclusive=lower_bound_inclusive,
            lower_bound=lower_bound,
            upper_bound_enabled=upper_bound_enabled,
            upper_bound_inclusive=upper_bound_inclusive,
            upper_bound=upper_bound,
        )
        self._append_attr(attr_type, md, atomic=atomic)

    def _append_attr(
        self,
        typ: str,
        md: _Metadata,
        atomic=None,
        union=None,
        pb_cls=None,
        col_params_binded_table=None,
    ):
        attr = AttributeDef(
            type=typ,
            name=md.name,
            desc=md.desc,
            prefixes=md.prefixes,
            atomic=atomic,
            union=union,
            custom_protobuf_cls=pb_cls,
            col_params_binded_table=col_params_binded_table,
            minor_min=md.minor_min,
            minor_max=md.minor_max,
        )
        self._attrs.append(attr)
        if typ not in [AttrType.ATTR_TYPE_UNSPECIFIED, AttrType.AT_STRUCT_GROUP]:
            self._attr_types[md.fullname] = typ

    @staticmethod
    def _check_list(field_type) -> tuple[bool, type]:
        origin = get_origin(field_type)
        if origin is list:
            args = get_args(field_type)
            if not args:
                raise ValueError("list must have type.")
            return (True, args[0])
        else:
            return (False, field_type)

    def _build_metadata(
        self, field: DField, prefixes: list[str], parent: _Metadata = None
    ) -> _Metadata:
        if field.name in RESERVED:
            raise ValueError(f"{field.name} is a reserved word.")

        if "md" not in field.metadata:
            raise ValueError(f"md not exist in {field.name}, {field.metadata}")
        md: _Metadata = field.metadata["md"]
        md.name = field.name
        md.type = field.type
        md.prefixes = prefixes
        md.fullname = Reflector._to_fullname(prefixes, field.name)

        assert (
            self._minor >= md.minor_min and self._minor >= md.minor_max
        ), f"{self._minor} shoule be greater than {md.minor_min} and {md.minor_max}"

        if parent != None:
            # inherit parent‘s minor_min version if it is zero
            if md.minor_min == 0:
                md.minor_min = parent.minor_min
            elif md.minor_min < parent.minor_min:
                raise ValueError(
                    f"minor version of {md.name} must be greater than or equal to {parent.minor_min}"
                )
        return md

    @staticmethod
    def _build_list_limit(is_list: bool, limit: Interval | None) -> tuple[int, int]:
        if not is_list and limit is None:
            # limit must be 1 if target type is not list
            return (1, 1)
        if limit is None:
            return (0, -1)

        limit.enforce_closed()
        list_min_length_inclusive = 0
        list_max_length_inclusive = -1
        if limit.lower != None:
            assert limit.lower >= 0, f"list min size should be 1"
            list_min_length_inclusive = int(limit.lower)
        if limit.upper != None:
            list_max_length_inclusive = int(limit.upper)
        return (list_min_length_inclusive, list_max_length_inclusive)

    @staticmethod
    def _to_attr_type(prim_type, is_list) -> str:
        if prim_type is float:
            return AttrType.AT_FLOATS if is_list else AttrType.AT_FLOAT
        elif prim_type is int:
            return AttrType.AT_INTS if is_list else AttrType.AT_INT
        elif prim_type is str:
            return AttrType.AT_STRINGS if is_list else AttrType.AT_STRING
        elif prim_type is bool:
            return AttrType.AT_BOOLS if is_list else AttrType.AT_BOOL
        else:
            return AttrType.ATTR_TYPE_UNSPECIFIED

    @staticmethod
    def _to_attr(v: Any, prim_type: type | None = None) -> Attribute:
        is_list = isinstance(v, list)
        if prim_type == None:
            if is_list:
                raise ValueError(f"unknown list primitive type for {v}")
            prim_type = type(v)

        if prim_type == bool:
            return Attribute(bs=v) if is_list else Attribute(b=v)
        elif prim_type == int:
            return Attribute(i64s=v) if is_list else Attribute(i64=v)
        elif prim_type == float:
            return Attribute(fs=v) if is_list else Attribute(f=v)
        elif prim_type == str:
            return Attribute(ss=v) if is_list else Attribute(s=v)
        else:
            raise ValueError(f"unsupported primitive type {prim_type}")

    @staticmethod
    def _to_fullname(prefixes: list, name: str) -> str:
        if prefixes is not None and len(prefixes) > 0:
            return "/".join(prefixes) + "/" + name
        else:
            return name

    @staticmethod
    def _force_dataclass(cls):
        if "__dataclass_params__" not in cls.__dict__:
            dataclass(cls)


class Definition:
    def __init__(
        self,
        cls: type[Component],
        domain: str,
        version: str,
        name: str = "",
        desc: str = None,
        labels: dict[str, str | bool | int | float] = None,
    ):
        if not issubclass(cls, Component):
            raise ValueError(f"{cls} must be subclass of Component")

        if name == "":
            name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

        if desc is None:
            desc = cls.__doc__ if cls.__doc__ is not None else ""

        if labels:
            for k, v in labels.items():
                v = str(v).lower() if isinstance(v, bool) else str(v)
                if len(k) > LABEL_LEN_MAX or len(v) > LABEL_LEN_MAX:
                    raise ValueError(
                        f"length of {k} or {v} must be less than {LABEL_LEN_MAX} in {name}:{version}"
                    )
                labels[k] = v

        root_package = cls.__module__.split(".")[0]

        self.name = name
        self.domain = domain
        self.version = version
        self.desc = clean_text(desc, no_line_breaks=False)
        self.labels = labels
        self.root_package = root_package

        self._minor = self.parse_minor(version)
        self._comp_cls = cls
        self._comp_id = self.build_id(domain, name, version)

        self._comp_def: ComponentDef = None
        self._inputs_map: dict[str, IoDef] = None
        self._attr_types: dict[str, AttrType] = None
        self.reflect()

    def __str__(self) -> str:
        return json_format.MessageToJson(self._comp_def, indent=0)

    @staticmethod
    def build_id(domain: str, name: str, version: str) -> str:
        return f"{domain}/{name}:{version}"

    @staticmethod
    def parse_id(comp_id: str) -> tuple[str, str, str]:
        pattern = r"(?P<domain>[^/]+)/(?P<name>[^:]+):(?P<version>.+)"
        match = re.match(pattern, comp_id)

        if match:
            return match.group("domain"), match.group("name"), match.group("version")
        else:
            raise ValueError(f"comp_id<{comp_id}> format is incorrect")

    @staticmethod
    def parse_minor(version: str) -> int:
        tokens = version.split(".")
        if len(tokens) != 3:
            raise ValueError(f"version must be in format of x.y.z, but got {version}")
        minor = int(tokens[1])
        assert minor >= 0, f"invalid minor<{minor}>"
        return minor

    @property
    def component_id(self) -> str:
        return self._comp_id

    @property
    def component_cls(self) -> type[Component]:
        return self._comp_cls

    @property
    def component_def(self) -> ComponentDef:
        if self._comp_def is None:
            self.reflect()
        return self._comp_def

    @staticmethod
    def _get_io(io_defs: list[IoDef], minor: int) -> list[IoDef]:
        result = []
        for io in io_defs:
            if minor < io.minor_min:
                continue
            if is_deprecated_minor(io.minor_max, minor):
                continue
            result.append(io)

        return result

    def get_input_defs(self, minor: int) -> list[IoDef]:
        return self._get_io(self.component_def.inputs, minor)

    def get_output_defs(self, minor: int) -> list[IoDef]:
        return self._get_io(self.component_def.outputs, minor)

    def reflect(self):
        r = Reflector(self._comp_cls, self.name, self._minor)
        r.reflect()
        self._comp_def = ComponentDef(
            name=self.name,
            desc=self.desc,
            domain=self.domain,
            version=self.version,
            labels=self.labels,
            inputs=r.get_inputs(),
            outputs=r.get_outputs(),
            attrs=r.get_attrs(),
        )
        self._inputs_map = {io.name: io for io in r.get_inputs()}
        self._attr_types = r.get_attr_types()

    def make_checkpoint_params(self, param: NodeEvalParam | dict) -> dict:
        kwargs, minor = self._to_kwargs(param)

        args = {}
        cls = self._comp_cls
        for name, field in cls.__dataclass_fields__.items():
            if name == MINOR_NAME:
                continue
            md: _Metadata = field.metadata["md"]
            if md.kind not in [
                FieldKind.BasicAttr,
                FieldKind.TableColumnAttr,
                FieldKind.Input,
            ]:
                continue
            if is_deprecated_minor(md.minor_max, minor) or not md.is_checkpoint:
                continue

            value = kwargs[md.fullname] if md.fullname in kwargs else md.default
            args[md.fullname] = value
        return args

    def make_component(
        self, param: NodeEvalParam | dict, check_exist: bool = True
    ) -> type[Component]:
        kwargs, minor = self._to_kwargs(param)

        creator = Creator(check_exist=check_exist)
        ins = creator.make(self._comp_cls, kwargs, minor)
        return ins

    def _to_kwargs(self, param: NodeEvalParam | dict) -> tuple[dict, int]:
        if isinstance(param, NodeEvalParam):
            kwargs = self.parse_param(param)
        elif isinstance(param, dict):
            kwargs = {}
            for k, v in param.items():
                self._fix_vertical_table(v)

                k = self._trim_input_prefix(k)
                kwargs[k] = v
        else:
            raise ValueError(f"unsupported param type {type(param)}")

        if MINOR_NAME not in kwargs:
            raise KeyError(f"kwargs must contain {MINOR_NAME}")
        minor = int(kwargs.pop(MINOR_NAME))

        return kwargs, minor

    def parse_param(
        self,
        param: NodeEvalParam,
        input_params: list[DistData] = None,
        output_params: list[str] | list[DistData] = None,
    ) -> dict:
        _, _, version = self.parse_id(param.comp_id)
        minor = self.parse_minor(version)

        attrs = self._parse_attrs(param)

        assert all(
            isinstance(item, DistData) for item in param.inputs
        ), f"type of inputs must be DistData"
        assert all(
            isinstance(item, str) for item in param.output_uris
        ), f"type of output_uris must be str"

        # parse input
        if input_params is None:
            input_params = param.inputs
        input_defs = self.get_input_defs(minor)
        input_size = len(input_params)
        if len(input_defs) > 0 and input_defs[-1].is_variable:
            in_var = input_defs[-1]
            expected_min = len(input_defs) - 1 + in_var.variable_min
            expected_max = len(input_defs) - 1 + in_var.variable_max
            if input_size < expected_min:
                raise ValueError(
                    f"input size<{input_size}> should be not less than {expected_min}"
                )
            if in_var.variable_max > -1 and input_size > expected_max:
                raise ValueError(
                    f"input size<{input_size}> should be not greater than {expected_max}"
                )
        elif len(input_defs) != input_size:
            raise ValueError(
                f"input size<{input_size}> mismatch, expect {input_defs} but got {input_params}"
            )

        inputs = {}

        for idx, io_def in enumerate(input_defs):
            if io_def.is_variable:
                assert idx == len(input_defs) - 1
                sub_params = input_params[idx:]
            else:
                sub_params = [input_params[idx]]

            # check type
            for in_param in sub_params:
                self._fix_vertical_table(in_param)
                if in_param.type not in io_def.types:
                    raise ValueError(
                        f"input type<{in_param.type}> mismatch, expect {io_def.types}"
                    )

            if io_def.is_variable:
                inputs[io_def.name] = sub_params
            else:
                inputs[io_def.name] = sub_params[0]

        # parse output
        if output_params is None:
            output_params = param.output_uris

        output_defs = self.get_output_defs(minor)
        assert len(output_defs) == len(
            output_params
        ), f"input size<{len(output_params)}> mismatch, expect {output_defs} but got {output_params}"

        outputs = {}
        for idx, io_def in enumerate(output_defs):
            output_data = output_params[idx]
            if isinstance(output_data, str):
                output = Output(output_data, None)
            elif isinstance(output_data, DistData):
                output = Output("", output_data)
            else:
                raise ValueError(
                    f"unsupport output type<{type(output_data)}>, name={io_def.name}"
                )
            outputs[io_def.name] = output

        return {**attrs, **inputs, **outputs, MINOR_NAME: minor}

    def _parse_attrs(self, param: NodeEvalParam) -> dict:
        attrs = {}
        for path, attr in zip(list(param.attr_paths), list(param.attrs)):
            path = self._trim_input_prefix(path)
            if path not in self._attr_types:
                raise KeyError(f"unknown attr key {path}")
            at = self._attr_types[path]
            attrs[path] = self._from_attr(attr, at)
        return attrs

    def _trim_input_prefix(self, p: str) -> str:
        if p.startswith("input/"):
            tokens = p.split("/", maxsplit=3)
            if len(tokens) != 3:
                raise ValueError(f"invalid input, {p}")
            assert (
                tokens[1] in self._inputs_map
            ), f"unknown input table name<{p}> in {self.component_id}"
            key = "_".join(tokens[1:])
            if key in self._attr_types:
                return key
            return tokens[2]
        return p

    @staticmethod
    def _from_attr(value: Attribute, at: AttrType) -> Any:
        if at == AttrType.ATTR_TYPE_UNSPECIFIED:
            raise ValueError("Type of Attribute is undefined.")
        elif at == AttrType.AT_FLOAT:
            return value.f
        elif at == AttrType.AT_INT:
            return value.i64
        elif at == AttrType.AT_STRING:
            return value.s
        elif at == AttrType.AT_BOOL:
            return value.b
        elif at == AttrType.AT_FLOATS:
            return list(value.fs)
        elif at == AttrType.AT_INTS:
            return list(value.i64s)
        elif at == AttrType.AT_BOOLS:
            return list(value.bs)
        elif at == AttrType.AT_CUSTOM_PROTOBUF:
            return value.s
        elif at == AttrType.AT_UNION_GROUP:
            return value.s
        elif at in [AttrType.AT_STRINGS, AttrType.AT_PARTY, AttrType.AT_COL_PARAMS]:
            return list(value.ss)
        elif at == AttrType.AT_STRUCT_GROUP:
            raise ValueError(f"AT_STRUCT_GROUP should be ignore")
        else:
            raise ValueError(f"unsupported type: {at}.")

    @staticmethod
    def _fix_vertical_table(dd: DistData):
        if not isinstance(dd, DistData):
            return
        if dd.type == DistDataType.OUTDATED_VERTICAL_TABLE:
            dd.type = DistDataType.VERTICAL_TABLE
