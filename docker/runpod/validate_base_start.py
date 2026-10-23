#!/usr/bin/env python3
"""Static contract check against the ACTUAL RunPod 1.4.1 startup.
Requires internet, Python and bash. No Docker/GPU needed.
"""
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

PINNED_URL = "https://raw.githubusercontent.com/runpod-workers/comfyui-base/1.4.1/start.sh"
root = Path(__file__).resolve().parent
with urllib.request.urlopen(PINNED_URL, timeout=30) as response:
    upstream = response.read().decode("utf-8")

with tempfile.TemporaryDirectory() as tmp:
    candidate = Path(tmp) / "start.sh"
    candidate.write_text(upstream)
    subprocess.run(
        [sys.executable, str(root / "patch_base_start.py"), str(candidate)],
        check=True,
    )
    subprocess.run(["bash", "-n", str(candidate)], check=True)
    patched = candidate.read_text()
    for required in (
        'JupyterLab not launched',
        'FileBrowser not launched',
        '--enable-manager',
        '/workspace/ComfyUI',
        'EXPECTED_CORE=v0.42.1',
        'JUPYTER_PASSWORD',
    ):
        assert required in patched, required
    # Missing/empty token starts no passwordless Jupyter service.
    assert 'if [[ -n "${JUPYTER_PASSWORD:-}" ]]; then' in patched
    # The old Manager checkout must be removed before runtime launch.
    assert 'rm -rf "$COMFYUI_DIR/custom_nodes/ComfyUI-Manager"' in patched
print("PASS: RunPod 1.4.1 patch anchors and bash syntax")
