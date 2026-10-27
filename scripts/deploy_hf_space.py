"""Update the authorized, existing CPU Space with a traceable source snapshot.

Only HF_TOKEN1 is used. No hardware, inference secrets or variables are changed.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

SPACE_ID = "Jaycee766/FrontierLab-Meta-Hackathon-2026"
ROOT = Path(__file__).resolve().parents[1]




def source_files(root: Path) -> dict[str, bytes]:
    """Allow-list public application assets; never upload a working directory."""
    files = {name: (root / name).read_bytes() for name in ("app.py", "requirements.txt")}
    for folder, suffixes in (("frontierlab", {".py"}), ("datasets", {".json"}),
                             ("docs", {".md", ".json"})):
        for path in sorted((root / folder).rglob("*")):
            if path.is_file() and path.suffix in suffixes and not path.is_symlink():
                relative = path.relative_to(root)
                if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
                    continue
                files[relative.as_posix()] = path.read_bytes()
    files["README.md"] = (root / "deploy/hf-space/README.md").read_bytes()
    files["Dockerfile"] = (root / "deploy/hf-space/Dockerfile").read_bytes()
    return files


def deploy(api, operation_class, *, root: Path, source_sha: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", source_sha):
        raise ValueError("A full checked-out GitHub source revision is required")
    if api.whoami()["name"] != "Jaycee766":
        raise PermissionError("HF token must belong to the authorized Space owner")
    info = api.space_info(SPACE_ID)
    runtime = api.get_space_runtime(SPACE_ID)
    if info.id != SPACE_ID or info.private or info.sdk != "docker":
        raise PermissionError("Only the existing public Docker target is authorized")
    hardware = getattr(runtime.hardware, "value", runtime.hardware)
    requested = getattr(runtime.requested_hardware, "value", runtime.requested_hardware)
    if hardware not in {"cpu-basic", None} or requested not in {"cpu-basic", None}:
        raise PermissionError("Deployment requires existing CPU Basic hardware")
    files = source_files(root)
    manifest = {p: hashlib.sha256(data).hexdigest() for p, data in sorted(files.items())}
    metadata = {
        "version": "v0.16", "source_sha": source_sha, "space_id": SPACE_ID,
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "file_sha256": manifest,
        "nvidia_secret_transferred": False, "hardware_changed": False,
    }
    files["deployment.json"] = (json.dumps(metadata, indent=2) + "\n").encode()
    commit = api.create_commit(
        repo_id=SPACE_ID, repo_type="space", parent_commit=info.sha,
        commit_message=f"Deploy FrontierLab v0.16 source {source_sha[:12]}",
        operations=[operation_class(path_in_repo=p, path_or_fileobj=data)
                    for p, data in sorted(files.items())],
    )
    return {"status": "HF_SOURCE_COMMITTED_BUILD_PENDING", "space_id": SPACE_ID,
            "source_sha": source_sha, "previous_space_sha": info.sha,
            "space_commit_sha": commit.oid,
            "space_url": f"https://huggingface.co/spaces/{SPACE_ID}",
            "app_url": "https://jaycee766-frontierlab-meta-hackathon-2026.hf.space",
            "files_uploaded": len(files), "nvidia_secret_transferred": False,
            "hardware_changed": False}


def main() -> None:
    if os.getenv("FRONTIERLAB_HF_DEPLOY") != "YES":
        raise PermissionError("Explicit HF deployment opt-in required")
    token = os.getenv("HF_TOKEN1", "")
    if not token:
        raise PermissionError("Existing HF_TOKEN1 deployment credential is required")
    from huggingface_hub import HfApi, CommitOperationAdd
    try:
        result = deploy(HfApi(token=token), CommitOperationAdd, root=ROOT,
                        source_sha=os.getenv("GITHUB_SHA", ""))
    except Exception as exc:
        # Keep provider responses and credential-bearing requests out of CI logs.
        raise RuntimeError(f"HF deployment failed ({type(exc).__name__}); no credential details logged") from None
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
