#!/usr/bin/env bash
# One command: get (or update), build and run LifeFlow Blood Camp on this server.
#   curl -fsSL https://raw.githubusercontent.com/grepx-support/grepx-database-server-orchastrator/blood-donation/install.sh | bash
# Optional, before `bash`:  SITE_URL=https://… ADMIN_EMAIL=… ADMIN_PASSWORD=… ADMIN_PHONE=… ADMIN_NAME=…
# Run it again any time to update. Needs: Linux, git, an SSH key on this server that GitHub accepts.
set -euo pipefail
REPO="${GREPX_REPO:-git@github.com:grepx-support/grepx-database-server-orchastrator.git}"
BRANCH=blood-donation
DIR="${GREPX_DIR:-$HOME/grepx-database-server-orchastrator}"
if [ -d "$DIR/.git" ]; then
  git -C "$DIR" fetch -q origin "$BRANCH" && git -C "$DIR" checkout -q "$BRANCH" && git -C "$DIR" pull -q --ff-only origin "$BRANCH"
else
  git clone -q -b "$BRANCH" "$REPO" "$DIR"
fi
cd "$DIR/orchestrator"
chmod +x ./*.sh
[ -d venv ] || ./setup.sh
./run.sh -p grepx-blood-donation
