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


from secretflow_spec import Reporter, VTable, VTableFieldKind, VTableFieldType
from secretflow_spec.core.dist_data.base import DistDataType
from secretflow_spec.core.dist_data.file import ObjectFile
from secretflow_spec.core.types import Version
from secretflow_spec.core.version import SPEC_VERSION
from secretflow_spec.v1.data_pb2 import (
    DistData,
    IndividualTable,
    TableSchema,
    VerticalTable,
)
from secretflow_spec.v1.report_pb2 import Report


def test_vtable_field():
    assert VTableFieldType.BOOL.is_bool()
    assert VTableFieldType.STR.is_string()
    assert VTableFieldType.INT.is_integer()
    assert VTableFieldType.INT32.is_integer()
    assert VTableFieldType.UINT32.is_integer()
    assert VTableFieldType.FLOAT.is_float()
    assert VTableFieldType.FLOAT32.is_float()
    assert VTableFieldType.is_same_type("int", "int64")

    assert VTableFieldKind.from_str("LABEL") == VTableFieldKind.LABEL
    assert VTableFieldKind.from_str("LABEL|FEATURE") == VTableFieldKind.FEATURE_LABEL

    assert str(VTableFieldKind.LABEL) == "LABEL"
    assert str(VTableFieldKind.FEATURE_LABEL) == "FEATURE|LABEL"


def test_vtable_indivitual():
    dd = DistData(
        name="input_ds",
        type=DistDataType.INDIVIDUAL_TABLE,
        data_refs=[
            DistData.DataRef(uri="xx", party="alice", format="csv"),
        ],
    )
    meta = IndividualTable(
        schema=TableSchema(
            id_types=["str"],
            ids=["id"],
            label_types=["float"],
            labels=["pred"],
            feature_types=["int", "int", "int"],
            features=["f1", "f2", "f3"],
        )
    )
    dd.meta.Pack(meta)

    t = VTable.from_distdata(dd, ["id", "f2", "pred"])
    assert t.columns == ["id", "f2", "pred"]

    t = VTable.from_distdata(dd)
    assert len(t.schemas) == 1

    assert t.select(["f3", "f1"]).columns == ["f3", "f1"]
    assert t.select_by_kinds(VTableFieldKind.LABEL).columns == ["pred"]
    assert t.drop(["f2"]).columns == ["id", "f1", "f3", "pred"]

    pb = t.to_distdata()
    assert pb.type == DistDataType.INDIVIDUAL_TABLE and len(pb.data_refs) == 1


def test_vtable_vertical():
    dd = DistData(
        name="input_ds",
        type=str(DistDataType.VERTICAL_TABLE),
        data_refs=[
            DistData.DataRef(uri="aa", party="alice", format="csv"),
            DistData.DataRef(uri="bb", party="bob", format="csv"),
        ],
    )

    meta = VerticalTable(
        schemas=[
            TableSchema(
                id_types=["str", "str"],
                ids=["a1", "a2"],
                feature_types=["float", "int"],
                features=["a3", "a4"],
                label_types=["int"],
                labels=["a5"],
            ),
            TableSchema(
                id_types=["str", "str"],
                ids=["b1", "b2"],
                feature_types=["float", "int"],
                features=["b3", "b4"],
                label_types=["int"],
                labels=["b5"],
            ),
        ]
    )
    dd.meta.Pack(meta)

    t = VTable.from_distdata(dd, columns=["a1", "a5", "a3"])
    assert t.columns == ["a1", "a5", "a3"]

    t = VTable.from_distdata(dd, columns=["a1", "a5", "a3", "b2", "b4"])
    assert t.columns == ["a1", "a5", "a3", "b2", "b4"]

    t = VTable.from_distdata(dd)
    assert set(t.columns) == set(
        [f"a{i+1}" for i in range(5)] + [f"b{i+1}" for i in range(5)]
    )
    t1 = t.select(["a2", "a1"])
    assert t1.columns == ["a2", "a1"]
    t2 = t.select(["a3", "a1", "b2", "b5"])
    assert t2.columns == ["a3", "a1", "b2", "b5"]
    t3 = t.drop(["a2", "a3", "b2", "b5"])
    assert set(t3.columns) == set(["a1", "a4", "a5", "b1", "b3", "b4"])
    t4 = t.drop(["a1"])
    columns = t.columns
    columns.remove("a1")
    assert t4.columns == columns
    t5 = t.select_by_kinds(VTableFieldKind.FEATURE)
    assert t5.columns == ["a3", "a4", "b3", "b4"]
    t6 = t.select_by_kinds(VTableFieldKind.FEATURE_LABEL)
    assert t6.columns == ["a3", "a4", "a5", "b3", "b4", "b5"]

    orders = ["bob", "alice"]
    assert list(t.sort_partitions(orders).schemas.keys()) == orders

    assert ["a1", "a2"] in t.schemas["alice"]
    assert "a1" in t.schemas["alice"]

    pb = t.to_distdata()
    assert pb.type == DistDataType.VERTICAL_TABLE and len(pb.data_refs) == 2
    assert pb.version == SPEC_VERSION


def test_report():
    r = Reporter(name="test_name", desc="test_desc")
    # add descriptions
    r.add_tab({"a": "a", "b": 1, "c": "0.1"})
    # add table
    r.add_tab({"a": [1, 2], "b": ["b1", "b2"], "c": [0.1, 0.2]})

    dd = r.to_distdata()
    assert len(dd.data_refs) == 0
    assert dd.version == SPEC_VERSION
    meta = Report()
    assert dd.meta.Unpack(meta)
    assert meta.name == "test_name" and meta.desc == "test_desc" and len(meta.tabs) == 2
    assert meta.tabs[0].divs[0].children[0].type == "descriptions"
    assert meta.tabs[1].divs[0].children[0].type == "table"


def test_file():
    file_version = Version(1, 0)
    public_info = {"a": 1, "b": 2}
    df = ObjectFile(
        name="xx",
        type="sf.model.sgb",
        data_refs=[
            DistData.DataRef(party="alice", uri="aa", format="pickle"),
            DistData.DataRef(party="bob", uri="aa", format="pickle"),
        ],
        version=file_version,
        public_info=public_info,
    )
    dd = df.to_distdata()
    assert dd.version == SPEC_VERSION
    nfile = ObjectFile.from_distdata(dd)
    assert nfile.version == file_version, nfile.public_info == public_info
