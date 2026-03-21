#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

"${script_dir}/run-in-env.sh" teach build "$1" --audience "${2:-teacher}" --lang "${3:-nb}" --format pdf
