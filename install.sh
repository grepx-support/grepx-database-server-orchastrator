#!/usr/bin/env bash
# Install or update LifeFlow Blood Camp on this server - run from this repo:   ./install.sh
# Updates this repo, clones/updates the four app repos, builds Nexus, sets up, migrates, starts and seeds.
# Needs: Linux, git, an SSH key on this server that GitHub accepts.
set -euo pipefail
cd "$(dirname "$0")"
git config core.fileMode false          # scripts committed from Windows: the chmod below is not a local change
git pull -q --ff-only || echo "(could not update this repo - continuing with what is checked out)"
cd orchestrator
# Debian/Ubuntu ship Python's venv separately. Test by really making one (importing ensurepip can succeed while
# creating a venv still fails), install python3.X-venv if needed, and drop a half-made venv from a failed run.
if ! [ -x venv/bin/python ] || ! venv/bin/python -m pip --version >/dev/null 2>&1; then
  rm -rf venv
  for py in python3.12 python3; do
    command -v "$py" >/dev/null 2>&1 || continue
    probe="$(mktemp -d)"
    if ! "$py" -m venv "$probe/v" >/dev/null 2>&1 && command -v apt-get >/dev/null 2>&1; then
      ver="$("$py" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
      SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO=sudo
      echo "installing python${ver}-venv (needed to create virtual environments)"
      $SUDO apt-get update -qq && $SUDO apt-get install -y -qq "python${ver}-venv" python3-venv
    fi
    rm -rf "$probe"
  done
fi
chmod +x ./*.sh ../install.sh 2>/dev/null || true
[ -d venv ] || bash setup.sh
bash run.sh -p grepx-blood-donation
