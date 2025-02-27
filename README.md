# SecretFlow Open Specification

SecretFlow Open Specification is a protocol stack designed for privacy-preserving applications.

## Spec

Please check [spec](docs/spec.md) and [intro](docs/intro.md).

## Build

### API Linter

After you modified protos, please check with API Linter.

```bash
go install github.com/googleapis/api-linter/cmd/api-linter@latest
sh secretflow_spec/protos/run_api_linter.sh
```
