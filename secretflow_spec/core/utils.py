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
from typing import Any

from secretflow_spec.core.dist_data.vtable import VTable
from secretflow_spec.core.version import SPEC_VERSION
from secretflow_spec.v1.component_pb2 import Attribute
from secretflow_spec.v1.data_pb2 import DistData
from secretflow_spec.v1.evaluation_pb2 import NodeEvalParam

LINEBREAK_REGEX = re.compile(r"((\r\n)|[\n\v])+")
TWO_LINEBREAK_REGEX = re.compile(r"((\r\n)|[\n\v])+((\r\n)|[\n\v])+")
MULTI_WHITESPACE_TO_ONE_REGEX = re.compile(r"\s+")
NONBREAKING_SPACE_REGEX = re.compile(r"(?!\n)\s+")


def normalize_whitespace(
    text: str, no_line_breaks=False, strip_lines=True, keep_two_line_breaks=False
):
    """
    Given ``text`` str, replace one or more spacings with a single space, and one
    or more line breaks with a single newline. Also strip leading/trailing whitespace.
    """
    if strip_lines:
        text = "\n".join([x.strip() for x in text.splitlines()])

    if no_line_breaks:
        text = MULTI_WHITESPACE_TO_ONE_REGEX.sub(" ", text)
    else:
        if keep_two_line_breaks:
            text = NONBREAKING_SPACE_REGEX.sub(
                " ", TWO_LINEBREAK_REGEX.sub(r"\n\n", text)
            )
        else:
            text = NONBREAKING_SPACE_REGEX.sub(" ", LINEBREAK_REGEX.sub(r"\n", text))

    return text.strip()


DOUBLE_QUOTE_REGEX = re.compile("|".join("«»“”„‟‹›❝❞❮❯〝〞〟＂"))
SINGLE_QUOTE_REGEX = re.compile("|".join("`´‘‘’’‛❛❜"))


def fix_strange_quotes(text):
    """
    Replace strange quotes, i.e., 〞with a single quote ' or a double quote " if it fits better.
    """
    text = SINGLE_QUOTE_REGEX.sub("'", text)
    text = DOUBLE_QUOTE_REGEX.sub('"', text)
    return text


def clean_text(text: str, no_line_breaks: bool = True) -> str:
    text = text.strip()
    text = normalize_whitespace(text, no_line_breaks)
    text = fix_strange_quotes(text)
    return text


_type_mapping: dict[str, type] = {
    "float": float,
    "bool": bool,
    "int": int,
    "str": str,
    # float
    "float16": float,
    "float32": float,
    "float64": float,
    # int
    "int8": int,
    "int16": int,
    "int32": int,
    "int64": int,
    "uint": int,
    "uint8": int,
    "uint16": int,
    "uint32": int,
    "uint64": int,
    # numpy specific type
    "float_": float,
    "bool_": bool,
    "int_": int,
    "str_": str,
    "object_": str,
    # others
    "double": float,
    "halffloat": float,
}


def to_type(dt) -> type:
    if not isinstance(dt, type):
        dt = type(dt)

    if dt.__name__ in _type_mapping:
        return _type_mapping[dt.__name__]
    else:
        raise ValueError(f"unsupported primitive type {dt}")


def to_attribute(v) -> Attribute:
    if isinstance(v, Attribute):
        return v

    is_list = isinstance(v, list)
    if is_list:
        assert len(v) > 0, f"Type cannot be inferred from an empty list"
        prim_type = type(v[0])
    else:
        prim_type = type(v)
        if prim_type not in [bool, int, float, str]:
            if prim_type.__name__ not in _type_mapping:
                raise ValueError(f"unsupported type {prim_type},{v}")
            if hasattr(v, "as_py"):
                method = getattr(v, "as_py")
                assert callable(method)
                v = method()
            else:
                prim_type = _type_mapping[prim_type.__name__]
                v = prim_type(v)

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


def build_node_eval_param(
    domain: str,
    name: str,
    version: str,
    attrs: dict[str, Any] = None,
    inputs: list[DistData | VTable] = None,
    output_uris: list[str] = None,
    checkpoint_uri: str = None,
) -> NodeEvalParam:
    """
    Used for constructing NodeEvalParam in unit tests.
    """

    attr_paths, attr_values = None, None
    if attrs:
        attr_paths, attr_values = [], []
        for k, v in attrs.items():
            attr_paths.append(k)
            attr_values.append(to_attribute(v))

    def _to_distdata(x) -> DistData:
        if isinstance(x, DistData):
            return x
        elif isinstance(x, VTable):
            return x.to_distdata()
        else:
            raise ValueError(f"invalid DistData type, {type(x)}")

    if inputs:
        inputs = [_to_distdata(dd) for dd in inputs]

    comp_id = f"{domain}/{name}:{version}"
    param = NodeEvalParam(
        version=SPEC_VERSION,
        comp_id=comp_id,
        attr_paths=attr_paths,
        attrs=attr_values,
        inputs=inputs,
        output_uris=output_uris,
        checkpoint_uri=checkpoint_uri,
    )
    return param
