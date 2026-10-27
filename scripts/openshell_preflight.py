"""Non-destructive checks. Never print vendor CLI stdout (may contain tokens)."""
import json
import platform
import shutil
import subprocess
import sys

def inspect(binary, args):
    path = shutil.which(binary)
    if not path:
        return {"found": False}
    try:
        result = subprocess.run([path, *args], capture_output=True, timeout=12, check=False)
        return {"found": True, "exit_code": result.returncode}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"found": True, "error_type": type(exc).__name__}

if __name__ == "__main__":
    status = {
        "platform": platform.platform(),
        "openshell_cli": inspect("openshell", ["--version"]),
        "openshell_gateway": inspect("openshell", ["status"]),
        "docker_cli": inspect("docker", ["--version"]),
        "docker_server": inspect("docker", ["info", "--format", "{{.ServerVersion}}"]),
        "meta_paid_api": "DISABLED",
        "note": "No credentials accessed. This is not a successful isolation test."
    }
    print(json.dumps(status, indent=2))
    sys.exit(0 if status["openshell_cli"].get("exit_code") == 0
                 and status["openshell_gateway"].get("exit_code") == 0 else 2)
