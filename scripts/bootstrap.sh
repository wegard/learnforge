#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

"${script_dir}/run-in-env.sh" python -m pip install -e ".[dev]"
"${script_dir}/run-in-env.sh" pre-commit install
"${script_dir}/run-in-env.sh" teach validate
