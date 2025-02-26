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


from secretflow_spec import Definition, build_node_eval_param


def test_build_node_eval_param():
    param = build_node_eval_param(
        domain="test_domain",
        name="test_name",
        version="1.0.0",
        attrs={"a": 1, "b": "s"},
    )

    domain, name, version = Definition.parse_id(param.comp_id)
    assert domain == "test_domain"
    assert name == "test_name"
    assert version == "1.0.0"
    assert Definition.parse_minor(version) == 0
