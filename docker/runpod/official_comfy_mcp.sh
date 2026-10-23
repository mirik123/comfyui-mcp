#!/usr/bin/env bash
# Run over authenticated SSH as an MCP stdio server. No public listener.
set -euo pipefail
COMFY_DIR="/workspace/runpod-slim/ComfyUI"
if [[ -n "$COMFYUI_WORKSPACE" ]]; then COMFY_DIR="$COMFYUI_WORKSPACE"; fi
if [[ ! -f "$COMFY_DIR/main.py" ]]; then
  echo "ComfyUI has not been initialized under $COMFY_DIR" >&2
  exit 1
fi
export COMFY_BIN=/opt/comfy-mcp-venv/bin/comfy
export COMFY_LOCAL_URL="http://127.0.0.1:8188"
"$COMFY_BIN" set-default "$COMFY_DIR" >&2
exec /opt/comfy-mcp-venv/bin/comfy-mcp "$@"
