#!/usr/bin/env bash
# Startup Antigravity — One-Command macOS & Linux Installer
# Usage:
#   ./install.sh            (copies or clones into ~/.gemini/config/plugins/startup-antigravity)
#   ./install.sh --symlink  (symlinks current repo for live local development)

set -euo pipefail

REPO_URL="https://github.com/petebiggam357/StartupAntigravity.git"
PLUGIN_DIR="${HOME}/.gemini/config/plugins/startup-antigravity"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Checking Python 3.10+..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required. Install Python 3.10+ and re-run."
  exit 1
fi

python3 -c 'import sys; assert sys.version_info >= (3, 10), f"Python 3.10+ required, found {sys.version}"'
echo "    Found $(python3 --version)"

mkdir -p "${HOME}/.gemini/config/plugins"

if [[ "${1:-}" == "--symlink" ]]; then
  echo "==> Symlinking ${SCRIPT_DIR} -> ${PLUGIN_DIR}"
  ln -sfn "${SCRIPT_DIR}" "${PLUGIN_DIR}"
elif [[ -f "${SCRIPT_DIR}/plugin.json" ]]; then
  if [[ -d "${PLUGIN_DIR}" && ! -L "${PLUGIN_DIR}" ]]; then
    echo "==> Updating existing plugin directory at ${PLUGIN_DIR}"
    if [[ -d "${PLUGIN_DIR}/.git" ]]; then
      git -C "${PLUGIN_DIR}" pull --ff-only || true
    else
      cp -R "${SCRIPT_DIR}/." "${PLUGIN_DIR}/"
    fi
  else
    echo "==> Installing local repo into ${PLUGIN_DIR}"
    rm -rf "${PLUGIN_DIR}"
    cp -R "${SCRIPT_DIR}" "${PLUGIN_DIR}"
  fi
else
  echo "==> Cloning Startup Antigravity into ${PLUGIN_DIR}"
  if [[ -d "${PLUGIN_DIR}/.git" ]]; then
    git -C "${PLUGIN_DIR}" pull --ff-only
  else
    git clone "${REPO_URL}" "${PLUGIN_DIR}"
  fi
fi

echo "==> Ensuring scripts are executable..."
chmod +x "${PLUGIN_DIR}/mcp_server/server.py" \
         "${PLUGIN_DIR}/hooks/"*.py \
         "${PLUGIN_DIR}/skills/pitch-deck-builder/scripts/build_deck.py" \
         "${PLUGIN_DIR}/skills/startup-kickstart/scripts/scaffold_startup.py" \
         "${PLUGIN_DIR}/skills/revenue-first-validation/scripts/build_landing_page.py" \
         "${PLUGIN_DIR}/skills/multi-ai-connectors/scripts/ai_connector.py" \
         "${PLUGIN_DIR}/skills/unit-economics-and-profit-os/scripts/build_dashboard.py"

echo "==> Running built-in self-test suite..."
(cd "${PLUGIN_DIR}" && python3 -m unittest discover -s tests -v)

echo ""
echo "SUCCESS! Startup Antigravity is installed at:"
echo "  ${PLUGIN_DIR}"
echo "Next step: Open Antigravity -> Additional Options (...) > MCP Servers > Refresh, then open a new folder!"
