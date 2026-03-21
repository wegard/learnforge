#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root_dir="$(cd -- "${script_dir}/.." && pwd)"
env_prefix="${LEARNFORGE_ENV_PREFIX:-${root_dir}/.micromamba}"
cache_home="${LEARNFORGE_XDG_CACHE_HOME:-${root_dir}/.cache}"

if [[ $# -eq 0 ]]; then
  echo "usage: $(basename "$0") <command> [args...]" >&2
  exit 64
fi

if [[ -d "${env_prefix}/conda-meta" ]]; then
  if ! command -v micromamba >/dev/null 2>&1; then
    echo "micromamba is required to run commands from ${env_prefix}" >&2
    exit 127
  fi
  mkdir -p "${cache_home}"
  export XDG_CACHE_HOME="${cache_home}"
  exec micromamba run -p "${env_prefix}" "$@"
fi

exec "$@"
