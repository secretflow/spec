#!/bin/bash
cd "$(dirname "$(readlink -f "$0")")"

FILE="secretflow_spec/version.py"
CACHE=$(cat "$FILE") 

rm -f dist/*.whl
python3 setup.py bdist_wheel 
rm -rf ./build ./secretflow_spec.egg-info 

echo "$CACHE" > "$FILE"