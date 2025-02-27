#!/bin/bash
cd "$(dirname "$(readlink -f "$0")")"

# set -x
set -e

# check to install protoc-26.1
PROTOC_DIR="protoc-26.1"
PROTOC_BIN="${PROTOC_DIR}/bin/protoc"
PROTOC_ZIP_NAME="protoc-26.1-linux-x86_64.zip"
DOWNLOAD_URL="https://github.com/protocolbuffers/protobuf/releases/download/v26.1/${PROTOC_ZIP_NAME}"

if [ ! -d "$PROTOC_DIR" ]; then
    echo "start download protoc"
    wget "$DOWNLOAD_URL"
    unzip "$PROTOC_ZIP_NAME" -d "./$PROTOC_DIR"
    rm -f $PROTOC_ZIP_NAME
fi

# check to install mypy-protobuf
mypy_installed_version=$(pip show mypy-protobuf 2>/dev/null | grep Version | awk '{print $2}')
mypy_required_version="3.6.0"

if [ "$mypy_installed_version" == "$mypy_required_version" ]; then
    echo "mypy-protobuf<$mypy_required_version> has installed."
else
    if [ -z "$mypy_installed_version" ]; then
        echo "mypy-protobuf not found"
    else
        echo "mypy-protobuf version mismatch, current is $mypy_installed_version, but required is $mypy_required_version"
        pip uninstall mypy-protobuf -y
    fi
    echo "start to install mypy-protobuf==$mypy_required_version"
    pip install mypy-protobuf==$mypy_required_version
fi

# build pb2.py
$PROTOC_BIN --proto_path="$PROTOC_DIR/include" --proto_path=. --python_out=../.. --mypy_out=../../ secretflow_spec/v1/*.proto