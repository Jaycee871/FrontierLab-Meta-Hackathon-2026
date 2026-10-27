"""Read-only hardware preflight. Exits 2 before downloads if resource estimate fails."""
import json
import os
import shutil
import subprocess
from frontierlab.hardware import assess

def ram_available():
    try:
        with open("/proc/meminfo", encoding="utf8") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return round(int(line.split()[1]) / 1048576, 2)
    except (ValueError, OSError, IndexError):
        pass
    return 0.0

def gpu_free():
    if not shutil.which("nvidia-smi"):
        return []
    try:
        run = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=10, check=True)
        return [round(int(line.strip()) / 1024, 2) for line in run.stdout.splitlines() if line.strip()]
    except (OSError, subprocess.SubprocessError, ValueError):
        return []

if __name__ == "__main__":
    ram = ram_available()
    disk = round(shutil.disk_usage(os.getcwd()).free / 1073741824, 2)
    gpu = gpu_free()
    state = assess(ram, disk, gpu)
    print(json.dumps({"available_ram_gib": ram, "free_disk_gib": disk,
                      "gpu_free_gib_per_device": gpu, "assessment": state,
                      "downloaded_model": False, "billed_api_called": False}, indent=2))
    if not state["can_attempt"]:
        raise SystemExit(2)
