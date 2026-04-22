#!/usr/bin/env bash
set -euo pipefail

package="@analyticscli/cli@preview"
user_prefix="${ANALYTICSCLI_NPM_PREFIX:-${HOME}/.local/analyticscli-npm}"

print_path_hint() {
  local bin_dir="$1"
  cat <<EOF
analyticscli was installed into:
  ${bin_dir}

For future shells, add this to your shell profile:
  export PATH="${bin_dir}:\$PATH"

For the current shell/session, run:
  export PATH="${bin_dir}:\$PATH"
EOF
}

if command -v analyticscli >/dev/null 2>&1; then
  echo "analyticscli already available: $(command -v analyticscli)"
  analyticscli --help >/dev/null
  exit 0
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required to install ${package}, but npm was not found." >&2
  exit 1
fi

echo "Installing AnalyticsCLI CLI from npm package ${package}"
set +e
global_output="$(npm install -g "${package}" 2>&1)"
global_exit=$?
set -e

if [[ ${global_exit} -ne 0 ]]; then
  if printf '%s' "${global_output}" | grep -Eiq 'EACCES|permission denied|access denied|operation not permitted'; then
    echo "Global npm install failed because of permissions. Falling back to user-local prefix: ${user_prefix}" >&2
    mkdir -p "${user_prefix}"
    npm install -g --prefix "${user_prefix}" "${package}"
    export PATH="${user_prefix}/bin:${PATH}"
  else
    printf '%s\n' "${global_output}" >&2
    exit "${global_exit}"
  fi
fi

if ! command -v analyticscli >/dev/null 2>&1; then
  echo "Installed ${package}, but analyticscli is still not on PATH." >&2
  if [[ -x "${user_prefix}/bin/analyticscli" ]]; then
    print_path_hint "${user_prefix}/bin" >&2
  else
    echo "Check your npm global bin directory with: npm prefix -g" >&2
  fi
  exit 1
fi

echo "analyticscli installed: $(command -v analyticscli)"
analyticscli --help >/dev/null
case "$(command -v analyticscli)" in
  "${user_prefix}/bin/"*)
    print_path_hint "${user_prefix}/bin"
    ;;
esac
