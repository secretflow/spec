#! /bin/bash
#
# Copyright 2023 Ant Group Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# spec.tmpl is adapted from https://github.com/pseudomuto/protoc-gen-doc/blob/master/examples/templates/grpc-md.tmpl.
docker run --rm -v $(pwd)/:/out \
                -v $(pwd)/../:/protos \
                pseudomuto/protoc-gen-doc \
                --doc_opt=/out/spec.tmpl,spec.md \
                secretflow/spec/v1/data.proto \
                secretflow/spec/v1/component.proto \
                secretflow/spec/v1/evaluation.proto \
                secretflow/spec/v1/report.proto \
