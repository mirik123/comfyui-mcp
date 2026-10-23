# syntax=docker/dockerfile:1
# Fork deployment: artokun/comfyui-mcp 0.52.206 + historical RunPod (0.52.203).
# CUDA 13 and PyTorch are provided by the official RunPod image.
FROM runpod/comfyui:1.4.1-cuda13.0

ARG COMFYUI_REF=v0.42.1
ARG COMFYUI_MANAGER_VERSION=4.2.2
ARG PANEL_REF=main
ARG PANEL_REPO=https://github.com/artokun/comfyui-mcp-panel.git

# Update the BAKED seed. RunPod's /start.sh copies this into
# /workspace/runpod-slim/ComfyUI and manages subsequent upgrades.
# A constraints file pins the image's CUDA-13 PyTorch stack.
RUN set -eux; \
    git -C /opt/comfyui-baked fetch --depth 1 origin "$COMFYUI_REF"; \
    git -C /opt/comfyui-baked checkout --force --detach FETCH_HEAD; \
    rm -rf /opt/comfyui-baked/custom_nodes/ComfyUI-Manager; \
    python3.12 -m pip install --no-cache-dir \
      -c /opt/comfyui-runtime-constraints.txt \
      -r /opt/comfyui-baked/requirements.txt; \
    python3.12 -m pip install --no-cache-dir \
      -c /opt/comfyui-runtime-constraints.txt \
      "comfyui_manager==$COMFYUI_MANAGER_VERSION"; \
    python3.12 -c 'import torch; assert torch.version.cuda and torch.version.cuda.startswith("13."), torch.version.cuda'; \
    git clone --depth 1 --branch "$PANEL_REF" "$PANEL_REPO" \
      /opt/comfyui-baked/custom_nodes/comfyui-mcp-panel; \
    if [ -f /opt/comfyui-baked/custom_nodes/comfyui-mcp-panel/requirements.txt ]; then \
      python3.12 -m pip install --no-cache-dir \
         -c /opt/comfyui-runtime-constraints.txt \
         -r /opt/comfyui-baked/custom_nodes/comfyui-mcp-panel/requirements.txt; \
    fi; \
    printf '\nCUSTOM_COMFYUI_REF=%s\nCUSTOM_MANAGER_VERSION=%s\nCUSTOM_PANEL_REF=%s\n' \
      "$COMFYUI_REF" "$COMFYUI_MANAGER_VERSION" "$PANEL_REF" \
      >> /opt/comfyui-baked/.runpod-bundle-version

# Official Comfy-Org/comfy-mcp: separate from artokun's Node.js MCP backend.
# Installs an on-demand stdio MCP server; NO additional public listening ports.
RUN python3.12 -m venv /opt/comfy-mcp-venv \
 && /opt/comfy-mcp-venv/bin/python -m pip install --no-cache-dir --upgrade pip \
 && /opt/comfy-mcp-venv/bin/python -m pip install --no-cache-dir \
      "comfy-cli>=1.14.0" comfy-mcp \
 && /opt/comfy-mcp-venv/bin/comfy --version \
 && /opt/comfy-mcp-venv/bin/comfy-mcp --version

# Preserve RunPod's native first-boot and upgrade logic. Fail build if its
# expected startup anchors change (do NOT accidentally start open Jupyter).
COPY patch_base_start.py /opt/comfyui-fork/patch_base_start.py
RUN python3.12 /opt/comfyui-fork/patch_base_start.py /start.sh \
 && bash -n /start.sh

COPY official_comfy_mcp.sh /usr/local/bin/comfy-mcp-runpod
RUN chmod 755 /usr/local/bin/comfy-mcp-runpod \
 && bash -n /usr/local/bin/comfy-mcp-runpod \
 && test -s /opt/comfyui-baked/custom_nodes/comfyui-mcp-panel/__init__.py
ENV COMFYUI_WORKSPACE=/workspace/runpod-slim/ComfyUI
EXPOSE 8188 22 8888 8080
# The base ENTRYPOINT ["/start.sh"] handles /workspace persistence.
