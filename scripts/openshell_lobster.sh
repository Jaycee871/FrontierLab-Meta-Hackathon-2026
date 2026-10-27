#!/usr/bin/env bash
# Manual, operator-run sandbox experiment on a compatible OpenShell host.
set -euo pipefail
SB="frontierlab-claw"
ACTION="$1"
case "$ACTION" in
  preflight) python3 scripts/openshell_preflight.py ;;
  launch)
    command -v openshell >/dev/null
    openshell status >/dev/null
    if ! openshell sandbox create --help 2>&1 | grep -q -- '--no-auto-providers'; then
      echo "CLI does not show --no-auto-providers: aborting safely." >&2
      exit 3
    fi
    echo "Launching interactive OpenClaw with no automatically attached credentials."
    echo "Do NOT input paid API keys or attach private folders."
    openshell sandbox create --name "$SB" --keep --no-auto-providers --from openclaw -- openclaw-start
    ;;
  inspect)
    openshell sandbox get "$SB"
    openshell policy get "$SB" --full
    openshell sandbox provider list "$SB"
    echo "OpenShell policy logs: openshell logs $SB --tail"
    ;;
  probe)
    echo "Testing harmless outbound request: failure alone does NOT prove containment."
    if openshell sandbox exec -n "$SB" -- /bin/sh -lc \
      'if command -v curl >/dev/null 2>&1; then curl --connect-timeout 3 --max-time 8 -fsS https://example.com >/dev/null; else echo "curl missing"; exit 8; fi'; then
      echo "WARNING: outbound request succeeded; containment expectation failed!" >&2
      exit 9
    else
      echo "No success. Require an explicit DENIED event in OpenShell logs to call this a policy block."
    fi
    ;;
  cleanup) openshell sandbox delete "$SB" ;;
  *)
    echo "Usage: bash scripts/openshell_lobster.sh preflight|launch|inspect|probe|cleanup"
    exit 2 ;;
esac
