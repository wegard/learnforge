#!/usr/bin/env bash
set -euo pipefail

teach build "$1" --audience "${2:-teacher}" --lang "${3:-nb}" --format slides-pdf
