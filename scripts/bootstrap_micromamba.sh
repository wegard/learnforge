#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root_dir="$(cd -- "${script_dir}/.." && pwd)"
env_prefix="${LEARNFORGE_ENV_PREFIX:-${root_dir}/.micromamba}"
environment_file="${root_dir}/environment.yml"
cache_home="${LEARNFORGE_XDG_CACHE_HOME:-${root_dir}/.cache}"

if ! command -v micromamba >/dev/null 2>&1; then
  echo "micromamba is required for this bootstrap path" >&2
  exit 127
fi

mkdir -p "${cache_home}"
export XDG_CACHE_HOME="${cache_home}"

if [[ -f "${env_prefix}/conda-meta/history" ]]; then
  micromamba env update --yes --prefix "${env_prefix}" --file "${environment_file}"
else
  micromamba create --yes --prefix "${env_prefix}" --file "${environment_file}"
fi

micromamba run -p "${env_prefix}" python -m pip install --upgrade pip
micromamba run -p "${env_prefix}" python -m pip install -e "${root_dir}[dev]"
micromamba run -p "${env_prefix}" pre-commit install

cat <<EOF
LearnForge micromamba environment is ready at:
  ${env_prefix}

Repo scripts and Make targets will use this environment automatically.

Manual usage:
  ${root_dir}/scripts/run-in-env.sh python -m pytest -q

Shell activation:
  eval "\$(micromamba shell hook --shell \$(basename "\${SHELL:-bash}"))"
  micromamba activate "${env_prefix}"
EOF
