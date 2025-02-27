# Copyright 2024 Ant Group Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from secretflow_spec import Component, Registry, register
from secretflow_spec.core.definition import Definition
from secretflow_spec.core.version import SPEC_VERSION


@register(
    domain="test",
    version="1.0.0",
    name="test_comp",
    labels={
        "sf.use.mpc": True,
        "sf.multi.party.computation": "true",
    },
)
class DemoCompnent(Component):
    def evaluate(self):
        print("eval")


def test_registry():
    definitions = Registry.get_definitions()
    keys = list(Registry.get_definition_keys())
    assert len(definitions) > 0 and len(definitions) == len(keys)
    first = Registry.get_definition_by_key(keys[0])
    assert first is not None
    assert Registry.get_definition(first.domain, first.name, first.version)
    assert Registry.get_definition_by_class(first.component_cls)
    assert Registry.get_definition_by_id(first.component_id)

    test_comp_def = Registry.get_definition_by_id("test/test_comp:1.0.0")
    assert test_comp_def
    labels = test_comp_def.component_def.labels
    assert (
        labels["sf.use.mpc"] == "true"
        and labels["sf.multi.party.computation"] == "true"
    )

    comp_list = Registry.build_comp_list_def("test", "test", definitions)
    comp_ids = [
        Definition.build_id(c.domain, c.name, c.version) for c in comp_list.comps
    ]
    assert sorted(comp_ids) == comp_ids
    assert comp_list.version == SPEC_VERSION
