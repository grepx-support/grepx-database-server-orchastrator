#!/usr/bin/env bash
# Install or update LifeFlow Blood Camp on this server - run from this repo:   ./install.sh
# Updates this repo, clones/updates the four app repos, builds Nexus, sets up, migrates, starts and seeds.
# Needs: Linux, git, an SSH key on this server that GitHub accepts.
set -euo pipefail
cd "$(dirname "$0")"
git pull -q --ff-only || echo "(could not update this repo - continuing with what is checked out)"
cd orchestrator
chmod +x ./*.sh
[ -d venv ] || ./setup.sh
./run.sh -p grepx-blood-donation
