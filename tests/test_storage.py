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


import os

import pytest

from secretflow_spec.core.storage import make_storage
from secretflow_spec.v1.data_pb2 import StorageConfig


def test_local():
    root_dir = os.path.dirname(__file__)
    s = make_storage(
        StorageConfig(
            type="local_fs", local_fs=StorageConfig.LocalFSConfig(wd=root_dir)
        )
    )
    file = "test_storage.py"
    p = s.get_full_path(file)
    assert p == __file__
    size = s.get_size(file)
    assert size > 0
    with s.get_reader(file) as r:
        data = r.read()
        assert len(data) > 0

    assert s.exists(file)

    not_exists_file = "not_exists_file"
    assert s.exists(not_exists_file) == False
    with pytest.raises(FileNotFoundError) as e:
        s.get_reader(not_exists_file)
    with pytest.raises(IsADirectoryError) as e:
        s.get_writer(root_dir)
    with pytest.raises(IsADirectoryError) as e:
        s.get_reader(root_dir)
