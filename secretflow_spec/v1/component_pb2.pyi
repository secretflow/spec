"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
Copyright 2023 Ant Group Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _AttrType:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _AttrTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_AttrType.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    ATTR_TYPE_UNSPECIFIED: _AttrType.ValueType  # 0
    """NOTE: ATTR_TYPE_UNSPECIFIED could be used as a child of a union struct
    with no further attribute(s).
    """
    AT_FLOAT: _AttrType.ValueType  # 1
    """Scalar types

    FLOAT
    """
    AT_INT: _AttrType.ValueType  # 2
    """INT"""
    AT_STRING: _AttrType.ValueType  # 3
    """STRING"""
    AT_BOOL: _AttrType.ValueType  # 4
    """BOOL"""
    AT_FLOATS: _AttrType.ValueType  # 5
    """List types

    FLOATS
    """
    AT_INTS: _AttrType.ValueType  # 6
    """INTS"""
    AT_STRINGS: _AttrType.ValueType  # 7
    """STRINGS"""
    AT_BOOLS: _AttrType.ValueType  # 8
    """BOOLS"""
    AT_STRUCT_GROUP: _AttrType.ValueType  # 9
    """Special types."""
    AT_UNION_GROUP: _AttrType.ValueType  # 10
    AT_CUSTOM_PROTOBUF: _AttrType.ValueType  # 11
    AT_PARTY: _AttrType.ValueType  # 12
    """A specialized AT_STRINGS."""
    AT_COL_PARAMS: _AttrType.ValueType  # 13
    """A specialized AT_STRINGS."""

class AttrType(_AttrType, metaclass=_AttrTypeEnumTypeWrapper):
    """Supported attribute types."""

ATTR_TYPE_UNSPECIFIED: AttrType.ValueType  # 0
"""NOTE: ATTR_TYPE_UNSPECIFIED could be used as a child of a union struct
with no further attribute(s).
"""
AT_FLOAT: AttrType.ValueType  # 1
"""Scalar types

FLOAT
"""
AT_INT: AttrType.ValueType  # 2
"""INT"""
AT_STRING: AttrType.ValueType  # 3
"""STRING"""
AT_BOOL: AttrType.ValueType  # 4
"""BOOL"""
AT_FLOATS: AttrType.ValueType  # 5
"""List types

FLOATS
"""
AT_INTS: AttrType.ValueType  # 6
"""INTS"""
AT_STRINGS: AttrType.ValueType  # 7
"""STRINGS"""
AT_BOOLS: AttrType.ValueType  # 8
"""BOOLS"""
AT_STRUCT_GROUP: AttrType.ValueType  # 9
"""Special types."""
AT_UNION_GROUP: AttrType.ValueType  # 10
AT_CUSTOM_PROTOBUF: AttrType.ValueType  # 11
AT_PARTY: AttrType.ValueType  # 12
"""A specialized AT_STRINGS."""
AT_COL_PARAMS: AttrType.ValueType  # 13
"""A specialized AT_STRINGS."""
global___AttrType = AttrType

@typing.final
class Attribute(google.protobuf.message.Message):
    """The value of an attribute"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    F_FIELD_NUMBER: builtins.int
    I64_FIELD_NUMBER: builtins.int
    S_FIELD_NUMBER: builtins.int
    B_FIELD_NUMBER: builtins.int
    FS_FIELD_NUMBER: builtins.int
    I64S_FIELD_NUMBER: builtins.int
    SS_FIELD_NUMBER: builtins.int
    BS_FIELD_NUMBER: builtins.int
    IS_NA_FIELD_NUMBER: builtins.int
    f: builtins.float
    """FLOAT"""
    i64: builtins.int
    """INT
    NOTE(junfeng): "is" is preserved by Python. Replaced with "i64".
    """
    s: builtins.str
    """STRING"""
    b: builtins.bool
    """BOOL"""
    is_na: builtins.bool
    """Indicates the value is missing explicitly."""
    @property
    def fs(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.float]:
        """lists

        FLOATS
        """

    @property
    def i64s(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.int]:
        """INTS"""

    @property
    def ss(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]:
        """STRINGS"""

    @property
    def bs(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.bool]:
        """BOOLS"""

    def __init__(
        self,
        *,
        f: builtins.float = ...,
        i64: builtins.int = ...,
        s: builtins.str = ...,
        b: builtins.bool = ...,
        fs: collections.abc.Iterable[builtins.float] | None = ...,
        i64s: collections.abc.Iterable[builtins.int] | None = ...,
        ss: collections.abc.Iterable[builtins.str] | None = ...,
        bs: collections.abc.Iterable[builtins.bool] | None = ...,
        is_na: builtins.bool = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["b", b"b", "bs", b"bs", "f", b"f", "fs", b"fs", "i64", b"i64", "i64s", b"i64s", "is_na", b"is_na", "s", b"s", "ss", b"ss"]) -> None: ...

global___Attribute = Attribute

@typing.final
class AttributeDef(google.protobuf.message.Message):
    """Describe an attribute.
    There are three kinds of attribute.
    - Atomic Attributes: a solid field for users to fill-in.
    - Struct Attributes: a group of closely related attributes(including atomic,
    union and struct attributes).
    - Union Attributes: a group of mutually exlusive attributes(including union,
    group and dummy atomic attributes). Users should select only one children to
    fill-in. An atmoic attribute with ATTR_TYPE_UNSPECIFIED AttrType is regarded
    as dummy, which represents a selection of union without further
    configurations.
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing.final
    class AtomicAttrDesc(google.protobuf.message.Message):
        """Extras for an atomic attribute.
        Including: `AT_FLOAT | AT_INT | AT_STRING | AT_BOOL | AT_FLOATS | AT_INTS |
        AT_STRINGS | AT_BOOLS`.
        """

        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        LIST_MIN_LENGTH_INCLUSIVE_FIELD_NUMBER: builtins.int
        LIST_MAX_LENGTH_INCLUSIVE_FIELD_NUMBER: builtins.int
        IS_OPTIONAL_FIELD_NUMBER: builtins.int
        DEFAULT_VALUE_FIELD_NUMBER: builtins.int
        ALLOWED_VALUES_FIELD_NUMBER: builtins.int
        LOWER_BOUND_ENABLED_FIELD_NUMBER: builtins.int
        LOWER_BOUND_FIELD_NUMBER: builtins.int
        LOWER_BOUND_INCLUSIVE_FIELD_NUMBER: builtins.int
        UPPER_BOUND_ENABLED_FIELD_NUMBER: builtins.int
        UPPER_BOUND_FIELD_NUMBER: builtins.int
        UPPER_BOUND_INCLUSIVE_FIELD_NUMBER: builtins.int
        list_min_length_inclusive: builtins.int
        """Only valid when type is `AT_FLOATS \\| AT_INTS \\| AT_STRINGS \\| AT_BOOLS`."""
        list_max_length_inclusive: builtins.int
        """Only valid when type is `AT_FLOATS \\| AT_INTS \\| AT_STRINGS \\| AT_BOOLS`."""
        is_optional: builtins.bool
        """If True, when Atmoic Attr is not provided or is_na, default_value would
        be used. Else, Atmoic Attr must be provided.
        """
        lower_bound_enabled: builtins.bool
        """Only valid when type is `AT_FLOAT \\| AT_INT \\| AT_FLOATS \\| AT_INTS `.
        If the attribute is a list, lower_bound is applied to each element.
        """
        lower_bound_inclusive: builtins.bool
        upper_bound_enabled: builtins.bool
        """Only valid when type is `AT_FLOAT \\| AT_INT \\| AT_FLOATS \\| AT_INTS `.
        If the attribute is a list, upper_bound is applied to each element.
        """
        upper_bound_inclusive: builtins.bool
        @property
        def default_value(self) -> global___Attribute:
            """A reasonable default for this attribute if the user does not supply a
            value.
            """

        @property
        def allowed_values(self) -> global___Attribute:
            """Only valid when type is `AT_FLOAT \\| AT_INT \\| AT_STRING \\| AT_FLOATS \\|
            AT_INTS \\| AT_STRINGS`.
            Please use list fields of AtomicParameter, i.e. `ss`, `i64s`, `fs`.
            If the attribute is a list, allowed_values is applied to each element.
            """

        @property
        def lower_bound(self) -> global___Attribute: ...
        @property
        def upper_bound(self) -> global___Attribute: ...
        def __init__(
            self,
            *,
            list_min_length_inclusive: builtins.int = ...,
            list_max_length_inclusive: builtins.int = ...,
            is_optional: builtins.bool = ...,
            default_value: global___Attribute | None = ...,
            allowed_values: global___Attribute | None = ...,
            lower_bound_enabled: builtins.bool = ...,
            lower_bound: global___Attribute | None = ...,
            lower_bound_inclusive: builtins.bool = ...,
            upper_bound_enabled: builtins.bool = ...,
            upper_bound: global___Attribute | None = ...,
            upper_bound_inclusive: builtins.bool = ...,
        ) -> None: ...
        def HasField(self, field_name: typing.Literal["allowed_values", b"allowed_values", "default_value", b"default_value", "lower_bound", b"lower_bound", "upper_bound", b"upper_bound"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing.Literal["allowed_values", b"allowed_values", "default_value", b"default_value", "is_optional", b"is_optional", "list_max_length_inclusive", b"list_max_length_inclusive", "list_min_length_inclusive", b"list_min_length_inclusive", "lower_bound", b"lower_bound", "lower_bound_enabled", b"lower_bound_enabled", "lower_bound_inclusive", b"lower_bound_inclusive", "upper_bound", b"upper_bound", "upper_bound_enabled", b"upper_bound_enabled", "upper_bound_inclusive", b"upper_bound_inclusive"]) -> None: ...

    @typing.final
    class UnionAttrGroupDesc(google.protobuf.message.Message):
        """Extras for a union attribute group."""

        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        DEFAULT_SELECTION_FIELD_NUMBER: builtins.int
        default_selection: builtins.str
        """The default selected child."""
        def __init__(
            self,
            *,
            default_selection: builtins.str = ...,
        ) -> None: ...
        def ClearField(self, field_name: typing.Literal["default_selection", b"default_selection"]) -> None: ...

    PREFIXES_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    DESC_FIELD_NUMBER: builtins.int
    TYPE_FIELD_NUMBER: builtins.int
    ATOMIC_FIELD_NUMBER: builtins.int
    UNION_FIELD_NUMBER: builtins.int
    CUSTOM_PROTOBUF_CLS_FIELD_NUMBER: builtins.int
    COL_PARAMS_BINDED_TABLE_FIELD_NUMBER: builtins.int
    MINOR_MIN_FIELD_NUMBER: builtins.int
    MINOR_MAX_FIELD_NUMBER: builtins.int
    name: builtins.str
    """Must be unique in the same level just like Linux file systems.
    Only `^[a-zA-Z0-9_.-]*$` is allowed.
    `input` and `output` are reserved.
    """
    desc: builtins.str
    type: global___AttrType.ValueType
    custom_protobuf_cls: builtins.str
    """Extras for custom protobuf attribute"""
    col_params_binded_table: builtins.str
    """Extras for COL_PARAMS"""
    minor_min: builtins.int
    """The attribute can appear in NodeEvalParam only if current minor is in [minor_min, minor_max]
    if current minor < minor_min, it's not supported,
    if minor_max != -1 and current minor > minor_max, it's a deprecated attribute
    """
    minor_max: builtins.int
    @property
    def prefixes(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]:
        """Indicates the ancestors of a node,
        e.g. `[name_a, name_b, name_c]` means the path prefixes of current
        Attribute is `name_a/name_b/name_c/`.
        Only `^[a-zA-Z0-9_.-]*$` is allowed.
        `input` and `output` are reserved.
        """

    @property
    def atomic(self) -> global___AttributeDef.AtomicAttrDesc: ...
    @property
    def union(self) -> global___AttributeDef.UnionAttrGroupDesc: ...
    def __init__(
        self,
        *,
        prefixes: collections.abc.Iterable[builtins.str] | None = ...,
        name: builtins.str = ...,
        desc: builtins.str = ...,
        type: global___AttrType.ValueType = ...,
        atomic: global___AttributeDef.AtomicAttrDesc | None = ...,
        union: global___AttributeDef.UnionAttrGroupDesc | None = ...,
        custom_protobuf_cls: builtins.str = ...,
        col_params_binded_table: builtins.str = ...,
        minor_min: builtins.int = ...,
        minor_max: builtins.int = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["atomic", b"atomic", "union", b"union"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["atomic", b"atomic", "col_params_binded_table", b"col_params_binded_table", "custom_protobuf_cls", b"custom_protobuf_cls", "desc", b"desc", "minor_max", b"minor_max", "minor_min", b"minor_min", "name", b"name", "prefixes", b"prefixes", "type", b"type", "union", b"union"]) -> None: ...

global___AttributeDef = AttributeDef

@typing.final
class IoDef(google.protobuf.message.Message):
    """Define an input/output for component."""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing.final
    class TableAttrDef(google.protobuf.message.Message):
        """An extra attribute for a table.

        If provided in a IoDef, e.g.
        ```json
        {
          "name": "feature",
          "types": [
              "int",
              "float"
          ],
          "col_min_cnt_inclusive": 1,
          "col_max_cnt": 3,
          "attrs": [
              {
                  "name": "bucket_size",
                  "type": "AT_INT"
              }
          ]
        }
        ```
        means after a user provide a table as IO, they should also specify
        cols as "feature":
        - col_min_cnt_inclusive is 1: At least 1 col to be selected.
        - col_max_cnt_inclusive is 3: At most 3 cols to be selected.
        And afterwards, user have to fill an int attribute called bucket_size for
        each selected cols.
        """

        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        NAME_FIELD_NUMBER: builtins.int
        DESC_FIELD_NUMBER: builtins.int
        TYPES_FIELD_NUMBER: builtins.int
        COL_MIN_CNT_INCLUSIVE_FIELD_NUMBER: builtins.int
        COL_MAX_CNT_INCLUSIVE_FIELD_NUMBER: builtins.int
        EXTRA_ATTRS_FIELD_NUMBER: builtins.int
        name: builtins.str
        """Must be unique among all attributes for the table."""
        desc: builtins.str
        col_min_cnt_inclusive: builtins.int
        """inclusive"""
        col_max_cnt_inclusive: builtins.int
        @property
        def types(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]:
            """Accepted col data types.
            Please check comments of TableSchema in data.proto.
            """

        @property
        def extra_attrs(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___AttributeDef]:
            """extra attribute for specified col."""

        def __init__(
            self,
            *,
            name: builtins.str = ...,
            desc: builtins.str = ...,
            types: collections.abc.Iterable[builtins.str] | None = ...,
            col_min_cnt_inclusive: builtins.int = ...,
            col_max_cnt_inclusive: builtins.int = ...,
            extra_attrs: collections.abc.Iterable[global___AttributeDef] | None = ...,
        ) -> None: ...
        def ClearField(self, field_name: typing.Literal["col_max_cnt_inclusive", b"col_max_cnt_inclusive", "col_min_cnt_inclusive", b"col_min_cnt_inclusive", "desc", b"desc", "extra_attrs", b"extra_attrs", "name", b"name", "types", b"types"]) -> None: ...

    NAME_FIELD_NUMBER: builtins.int
    DESC_FIELD_NUMBER: builtins.int
    TYPES_FIELD_NUMBER: builtins.int
    ATTRS_FIELD_NUMBER: builtins.int
    IS_OPTIONAL_FIELD_NUMBER: builtins.int
    IS_VARIABLE_FIELD_NUMBER: builtins.int
    VARIABLE_MIN_FIELD_NUMBER: builtins.int
    VARIABLE_MAX_FIELD_NUMBER: builtins.int
    MINOR_MIN_FIELD_NUMBER: builtins.int
    MINOR_MAX_FIELD_NUMBER: builtins.int
    name: builtins.str
    """should be unique among all IOs of the component."""
    desc: builtins.str
    is_optional: builtins.bool
    is_variable: builtins.bool
    """if the input io is variable, it must be the last one and size must be in [variable_min, variable_max]"""
    variable_min: builtins.int
    variable_max: builtins.int
    minor_min: builtins.int
    """The io input/output can appear in NodeEvalParam only if current minor is in [minor_min, minor_max]
    if current minor < minor_min, it's not supported,
    if minor_max != -1 and current minor > minor_max, it's a deprecated io input/output
    """
    minor_max: builtins.int
    @property
    def types(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]:
        """Must be one of DistData.type in data.proto"""

    @property
    def attrs(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___IoDef.TableAttrDef]:
        """Only valid for tables.
        The attribute path for a TableAttrDef is `{input\\|output}/{IoDef
        name}/{TableAttrDef name}`.
        """

    def __init__(
        self,
        *,
        name: builtins.str = ...,
        desc: builtins.str = ...,
        types: collections.abc.Iterable[builtins.str] | None = ...,
        attrs: collections.abc.Iterable[global___IoDef.TableAttrDef] | None = ...,
        is_optional: builtins.bool = ...,
        is_variable: builtins.bool = ...,
        variable_min: builtins.int = ...,
        variable_max: builtins.int = ...,
        minor_min: builtins.int = ...,
        minor_max: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["attrs", b"attrs", "desc", b"desc", "is_optional", b"is_optional", "is_variable", b"is_variable", "minor_max", b"minor_max", "minor_min", b"minor_min", "name", b"name", "types", b"types", "variable_max", b"variable_max", "variable_min", b"variable_min"]) -> None: ...

global___IoDef = IoDef

@typing.final
class ComponentDef(google.protobuf.message.Message):
    """The definition of a comp."""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing.final
    class LabelsEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: builtins.str
        value: builtins.str
        def __init__(
            self,
            *,
            key: builtins.str = ...,
            value: builtins.str = ...,
        ) -> None: ...
        def ClearField(self, field_name: typing.Literal["key", b"key", "value", b"value"]) -> None: ...

    DOMAIN_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    VERSION_FIELD_NUMBER: builtins.int
    DESC_FIELD_NUMBER: builtins.int
    LABELS_FIELD_NUMBER: builtins.int
    ATTRS_FIELD_NUMBER: builtins.int
    INPUTS_FIELD_NUMBER: builtins.int
    OUTPUTS_FIELD_NUMBER: builtins.int
    domain: builtins.str
    """Namespace of the comp."""
    name: builtins.str
    """Should be unique among all comps of the same domain."""
    version: builtins.str
    """Version of the comp."""
    desc: builtins.str
    """Description of the comp."""
    @property
    def labels(self) -> google.protobuf.internal.containers.ScalarMap[builtins.str, builtins.str]:
        """Static label infomations of the comp.
        e.g., {"sf.use.mpc":"true", "sf.multi.party.computation":"true"}
        """

    @property
    def attrs(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___AttributeDef]: ...
    @property
    def inputs(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___IoDef]: ...
    @property
    def outputs(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___IoDef]: ...
    def __init__(
        self,
        *,
        domain: builtins.str = ...,
        name: builtins.str = ...,
        version: builtins.str = ...,
        desc: builtins.str = ...,
        labels: collections.abc.Mapping[builtins.str, builtins.str] | None = ...,
        attrs: collections.abc.Iterable[global___AttributeDef] | None = ...,
        inputs: collections.abc.Iterable[global___IoDef] | None = ...,
        outputs: collections.abc.Iterable[global___IoDef] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["attrs", b"attrs", "desc", b"desc", "domain", b"domain", "inputs", b"inputs", "labels", b"labels", "name", b"name", "outputs", b"outputs", "version", b"version"]) -> None: ...

global___ComponentDef = ComponentDef

@typing.final
class CompListDef(google.protobuf.message.Message):
    """A list of components"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    VERSION_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    DESC_FIELD_NUMBER: builtins.int
    COMPS_FIELD_NUMBER: builtins.int
    version: builtins.str
    """The version of spec, format is {major}.{minor}
    the different major version are not compatible
    the different minor version should be forward compatible, In other words, you can only add fields and cannot modify or delete fields.
    """
    name: builtins.str
    desc: builtins.str
    @property
    def comps(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___ComponentDef]: ...
    def __init__(
        self,
        *,
        version: builtins.str = ...,
        name: builtins.str = ...,
        desc: builtins.str = ...,
        comps: collections.abc.Iterable[global___ComponentDef] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["comps", b"comps", "desc", b"desc", "name", b"name", "version", b"version"]) -> None: ...

global___CompListDef = CompListDef
