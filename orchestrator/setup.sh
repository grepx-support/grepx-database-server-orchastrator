#!/usr/bin/env bash
# orchestrator/setup.sh - the orchestrator's own Python environment (orchestrator/venv). install.sh runs it; safe to re-run.
set -euo pipefail
cd "$(dirname "$0")"

say() { printf '%s %-5s [%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" "setup" "$2"; }
die() { say ERROR "$1"; exit 1; }
venv_python() { if [ -x venv/bin/python ]; then echo venv/bin/python; else echo venv/Scripts/python.exe; fi; }   # Linux / Git Bash

if [ -x "$(venv_python)" ] && "$(venv_python)" -c "import yaml" >/dev/null 2>&1; then
  say OK "orchestrator venv ready"; exit 0
fi
rm -rf venv                                   # half-made venv from a failed run

PY=""
for candidate in python3.12 python3 python; do command -v "$candidate" >/dev/null 2>&1 && { PY="$candidate"; break; }; done
[ -n "$PY" ] || die "no python3 found - install Python 3.10+"

# Debian/Ubuntu ship venv separately; importing ensurepip can succeed while creating a venv fails, so really try one.
probe="$(mktemp -d)"
if ! "$PY" -m venv "$probe/v" >/dev/null 2>&1; then
  command -v apt-get >/dev/null 2>&1 || die "$PY cannot create virtual environments - install its venv package"
  ver="$("$PY" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
  SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO=sudo
  say INFO "installing python${ver}-venv"
  $SUDO apt-get update -qq && $SUDO apt-get install -y -qq "python${ver}-venv" python3-venv >/dev/null || die "could not install python${ver}-venv"
fi
rm -rf "$probe"

say INFO "creating orchestrator venv ($PY)"
"$PY" -m venv venv || die "could not create orchestrator/venv"
"$(venv_python)" -m pip install -q --upgrade pip || die "pip upgrade failed"
"$(venv_python)" -m pip install -q -r requirements.txt || die "could not install orchestrator/requirements.txt"
say OK "orchestrator venv ready"
