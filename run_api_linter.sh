#!/bin/bash
PROTO_FOLDER="secretflow/"
AIP_LINTER_PATH=$(which api-linter)

failures=0


for file in $(find $PROTO_FOLDER -name '*.proto'); do
  lint_output=$("$AIP_LINTER_PATH" "$file" --config api_linter_config.json)

  if echo "$lint_output" | grep -iq "problems: \[\]"; then
    echo "[Scucess] $file."
  else
    echo "[Failure] $file:"
    echo "$lint_output"
    ((failures++))
  fi
done

exit $failures
