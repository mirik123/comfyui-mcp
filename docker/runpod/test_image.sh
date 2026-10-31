#!/usr/bin/env bash
# Post-build Docker smoke; no GPU required. Does not run real ComfyUI startup.
set -euo pipefail
IMAGE="$1"
docker image inspect "$IMAGE" >/dev/null
docker run --rm --entrypoint bash "$IMAGE" -ec '
  test -s /opt/comfyui-baked/main.py
  grep -q CUSTOM_COMFYUI_REF=v0.42.1 /opt/comfyui-baked/.runpod-bundle-version
  test -s /opt/comfyui-baked/custom_nodes/comfyui-mcp-panel/__init__.py
  test -s /opt/comfyui-baked/custom_nodes/ComfyUI-RunpodDirect/__init__.py
  test -s /opt/comfyui-baked/custom_nodes/ComfyUI-MiniMaxH3-Context-Loop/__init__.py
  test -s /opt/comfyui-baked/custom_nodes/ComfyUI_MiniMax_H3_Extender/__init__.py
  test -s /opt/comfyui-baked/custom_nodes/ComfyUI-MiniMaxH3_LatentUpscaler/__init__.py
  test -s /opt/comfyui-baked/custom_nodes/ComfyUI-H3-Motion-Context-MultiRef/__init__.py
  test -s /opt/comfyui-baked/custom_nodes/ComfyUI-H3-Latent-Upscaler-Mamad8/__init__.py
  test "$(git -C /opt/comfyui-baked/custom_nodes/ComfyUI-RunpodDirect branch --show-current)" = main
  test "$(git -C /opt/comfyui-baked/custom_nodes/ComfyUI-RunpodDirect rev-parse --abbrev-ref --symbolic-full-name "@{upstream}")" = origin/main
  test -x /opt/comfy-mcp-venv/bin/comfy-mcp
  test -x /opt/comfy-mcp-venv/bin/comfy
  bash -n /start.sh
  bash -n /usr/local/bin/comfy-mcp-runpod
  grep -q "JupyterLab not launched" /start.sh
  grep -q "FileBrowser not launched" /start.sh
  python3.12 -c "import torch; assert torch.version.cuda.startswith(\"13.\")"
'
VOL="runpod-smoke-$$"
trap 'docker volume rm -f "$VOL" >/dev/null 2>&1 || true' EXIT
docker volume create "$VOL" >/dev/null
for pass in cold warm; do
  docker run --rm --entrypoint bash -v "$VOL:/workspace" "$IMAGE" -ec '
    mkdir -p /workspace/runpod-slim
    D=/workspace/runpod-slim/ComfyUI
    if [ ! -d "$D" ]; then cp -a /opt/comfyui-baked "$D"; fi
    if [ ! -d "$D/.venv-cu128" ]; then
       python3.12 -m venv --system-site-packages "$D/.venv-cu128"
    fi
    test -s "$D/main.py"
    test -s "$D/custom_nodes/comfyui-mcp-panel/__init__.py"
    test -s "$D/custom_nodes/ComfyUI-RunpodDirect/__init__.py"
    test -s "$D/custom_nodes/ComfyUI-MiniMaxH3-Context-Loop/__init__.py"
    test -s "$D/custom_nodes/ComfyUI_MiniMax_H3_Extender/__init__.py"
    test -s "$D/custom_nodes/ComfyUI-MiniMaxH3_LatentUpscaler/__init__.py"
    test -s "$D/custom_nodes/ComfyUI-H3-Motion-Context-MultiRef/__init__.py"
    test -s "$D/custom_nodes/ComfyUI-H3-Latent-Upscaler-Mamad8/__init__.py"
    test "$(git -C "$D/custom_nodes/ComfyUI-RunpodDirect" rev-parse --abbrev-ref --symbolic-full-name "@{upstream}")" = origin/main
    test -x "$D/.venv-cu128/bin/python"
    if [ -f "$D/persistent.txt" ]; then
      grep -qx survived "$D/persistent.txt"
    else
      echo survived > "$D/persistent.txt"
    fi
    if [ ! -e /workspace/ComfyUI ]; then ln -s "$D" /workspace/ComfyUI; fi
    test -s /workspace/ComfyUI/main.py
  '
done
echo "PASS: image artifacts and simulated /workspace persistence"
echo "NOTE: live startup, CUDA and LTX renders need a RunPod GPU test."
