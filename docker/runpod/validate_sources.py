#!/usr/bin/env python3
"""Static source check, not an actual Docker or GPU test."""
from pathlib import Path
import subprocess
import sys

d = Path(__file__).resolve().parent
docker = (d / "Dockerfile").read_text()
patch = (d / "patch_base_start.py").read_text()
for key in ("FROM runpod/comfyui:1.4.1-cuda13.0", "ARG COMFYUI_REF=v0.42.1",
            "comfyui_manager", "comfy-cli>=1.14.0",
            "comfy-mcp", "COPY patch_base_start.py",
            "ARG RUNPODDIRECT_BRANCH=main", "ComfyUI-RunpodDirect",
            "--single-branch --branch", "origin/$RUNPODDIRECT_BRANCH"):
    assert key in docker, key
for key in ("JUPYTER_PASSWORD", "FILEBROWSER_PASSWORD",
            "/workspace/ComfyUI", "--enable-manager"):
    assert key in patch, key
for name in ("test_image.sh", "official_comfy_mcp.sh"):
    subprocess.run(["bash", "-n", str(d / name)], check=True)
subprocess.run([sys.executable, "-m", "py_compile",
                str(d / "patch_base_start.py")], check=True)
work = (d.parent.parent / ".github/workflows/build-runpod-image.yml").read_text()
assert "push: false" in work, "Do not auto-push an untested image"
print("STATIC TESTS PASS; full Docker and GPU tests remain unverified")
