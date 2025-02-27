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


from collections import defaultdict
from typing import Iterable

from secretflow_spec.core.component import Component
from secretflow_spec.core.definition import Definition
from secretflow_spec.core.version import SPEC_VERSION
from secretflow_spec.v1.component_pb2 import CompListDef

_reg_defs_by_key: dict[str, Definition] = {}
_reg_defs_by_cls: dict[str, Definition] = {}
_reg_defs_by_pkg: dict[str, list[Definition]] = defaultdict(list)


def _parse_major(version: str) -> str:
    tokens = version.split(".")
    if len(tokens) != 3:
        raise ValueError(f"version must be in format of x.y.z, but got {version}")
    return tokens[0]


def _gen_reg_key(domain: str, name: str, version: str) -> str:
    return f"{domain}/{name}:{_parse_major(version)}"


def _gen_class_id(cls: Component | type[Component]) -> str:
    if isinstance(cls, Component):
        cls = type(cls)
    return f"{cls.__module__}:{cls.__qualname__}"


class Registry:
    @staticmethod
    def register(d: Definition):
        key = _gen_reg_key(d.domain, d.name, d.version)
        if key in _reg_defs_by_key:
            raise ValueError(f"{key} is already registered")
        class_id = _gen_class_id(d.component_cls)
        _reg_defs_by_key[key] = d
        _reg_defs_by_cls[class_id] = d
        _reg_defs_by_pkg[d.root_package].append(d)

    @staticmethod
    def unregister(domain: str, name: str, version: str) -> bool:
        key = _gen_reg_key(domain, name, version)
        if key not in _reg_defs_by_key:
            return False
        d = _reg_defs_by_key.pop(key)
        class_id = _gen_class_id(d.component_cls)
        del _reg_defs_by_cls[class_id]
        _reg_defs_by_pkg[d.root_package].remove(d)
        return True

    @staticmethod
    def get_definition(domain: str, name: str, version: str) -> Definition:
        key = _gen_reg_key(domain, name, version)
        return _reg_defs_by_key.get(key)

    @staticmethod
    def get_definitions(root_pkg: str = None) -> Iterable[Definition]:
        if root_pkg and root_pkg != "*":
            return _reg_defs_by_pkg.get(root_pkg, None)

        return _reg_defs_by_key.values()

    @staticmethod
    def get_definition_keys() -> Iterable[str]:
        return _reg_defs_by_key.keys()

    @staticmethod
    def get_definition_by_key(key: str) -> Definition:
        return _reg_defs_by_key.get(key)

    @staticmethod
    def get_definition_by_id(id: str) -> Definition:
        prefix, version = id.split(":")
        key = f"{prefix}:{_parse_major(version)}"
        comp_def = _reg_defs_by_key.get(key)

        return comp_def

    @staticmethod
    def get_definition_by_class(cls: Component | type[Component]) -> Definition:
        class_id = _gen_class_id(cls)
        return _reg_defs_by_cls.get(class_id)

    @staticmethod
    def build_comp_list_def(
        name: str,
        desc: str,
        components: Iterable[Definition],
        version: str = SPEC_VERSION,
    ) -> CompListDef:
        comps = [d.component_def for d in components]
        comps = sorted(comps, key=lambda k: (k.domain, k.name, k.version))
        return CompListDef(name=name, desc=desc, version=version, comps=comps)


def register(
    domain: str,
    version: str,
    name: str = "",
    desc: str = None,
    labels: dict[str, str | bool | int | float] = None,
):
    if domain == "" or version == "":
        raise ValueError(
            f"domain<{domain}> and version<{version}> cannot be empty in register"
        )

    def wrap(cls):
        d = Definition(cls, domain, version, name, desc, labels=labels)
        Registry.register(d)
        return cls

    return wrap
