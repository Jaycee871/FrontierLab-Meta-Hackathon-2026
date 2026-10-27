"""No network calls or downloads; conservative 17 GB GGUF resource estimates."""
def assess(ram_gib, disk_gib, gpu_free_gib):
    disk_ok = disk_gib >= 23
    gpu_ok = (sum(gpu_free_gib) >= 22 and
              (max(gpu_free_gib, default=0) >= 22 or
               len([v for v in gpu_free_gib if v >= 8]) >= 2))
    cpu_ok = ram_gib >= 24
    return {"can_attempt": disk_ok and (cpu_ok or gpu_ok),
            "gpu_candidate": disk_ok and gpu_ok,
            "cpu_candidate": disk_ok and cpu_ok,
            "note": "Preflight only: loading, speed and accuracy remain unverified."}
