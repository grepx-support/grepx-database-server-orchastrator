#!/usr/bin/env bash
# Install or update a GrepX project on this server - each project gets its own folder here, with its own repos and Nexus.
#   ./install.sh blood-donation     install / update one project   (into ./blood-donation/)
#   ./install.sh all                every project that is not skip: true
#   ./install.sh -l                 list the projects               ./install.sh -h   this help
#   add --fetch-only to only clone/update the repos.  Projects: orchestrator/projects/<name>.yaml
set -euo pipefail
cd "$(dirname "$0")"

say() { printf '%s %-5s [%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" "install" "$2"; }
die() { say ERROR "$1"; exit 1; }

projects() {   # name, state and description of every project file (no Python needed)
  for f in orchestrator/projects/*.yaml; do
    [ -f "$f" ] || continue
    name="$(basename "$f" .yaml)"
    desc="$(sed -n 's/^description:[[:space:]]*//p' "$f" | head -1)"
    state="ready"
    if grep -qE '^skip:[[:space:]]*true' "$f"; then state="skip"; elif [ -d "$name" ]; then state="installed"; fi
    printf '  %-20s %-10s %s\n' "$name" "$state" "$desc"
  done
}
usage() { sed -n '2,6p' "$0" | sed 's/^# \{0,1\}//'; echo; echo "Projects:"; projects; }

case "${1:-}" in
  ""|-h|--help) usage; exit 0 ;;
  -l|--list) echo "Projects:"; projects; exit 0 ;;
esac
TARGET="$1"; shift
if [ "$TARGET" != all ]; then
  [ -f "orchestrator/projects/$TARGET.yaml" ] || { usage; die "unknown project '$TARGET'"; }
  grep -qE '^skip:[[:space:]]*true' "orchestrator/projects/$TARGET.yaml" \
    && die "'$TARGET' is skip: true in orchestrator/projects/$TARGET.yaml - set it to false to install it"
fi

git config core.fileMode false 2>/dev/null || true      # scripts committed from Windows: chmod is not a local change
if git pull -q --ff-only 2>/dev/null; then say OK "orchestrator up to date"; else say WARN "could not update the orchestrator - using what is checked out"; fi
chmod +x install.sh orchestrator/*.sh 2>/dev/null || true

bash orchestrator/setup.sh
VPY=orchestrator/venv/bin/python; [ -x "$VPY" ] || VPY=orchestrator/venv/Scripts/python.exe
if [ "$TARGET" = all ]; then "$VPY" orchestrator/orchestrator.py -a "$@"; else "$VPY" orchestrator/orchestrator.py -p "$TARGET" "$@"; fi
