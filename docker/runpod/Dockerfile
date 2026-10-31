# syntax=docker/dockerfile:1
# artokun/comfyui-mcp v0.52.206 RunPod deployment.
# PINNED official CUDA 13 base (runpod-workers/comfyui-base tag 1.4.1).
FROM runpod/comfyui:1.4.1-cuda13.0

ARG COMFYUI_REF=v0.42.1
ARG COMFYUI_MANAGER_VERSION=4.2.2
ARG PANEL_REF=main
ARG PANEL_REPO=https://github.com/artokun/comfyui-mcp-panel.git
ARG RUNPODDIRECT_BRANCH=main
ARG RUNPODDIRECT_REPO=https://github.com/MadiatorLabs/ComfyUI-RunpodDirect.git
ARG H3_CONTEXT_LOOP_REPO=https://github.com/ethanfel/ComfyUI-MiniMaxH3-Context-Loop.git
ARG H3_EXTENDER_REPO=https://github.com/tritant/ComfyUI_MiniMax_H3_Extender.git
ARG H3_LATENT_UPSCALER_REPO=https://github.com/Tr1dae/ComfyUI-MiniMaxH3_LatentUpscaler.git
ARG H3_MOTION_CONTEXT_REPO=https://github.com/seitanism/ComfyUI-H3-Motion-Context-MultiRef.git
ARG H3_MAMAD8_UPSCALER_REPO=https://github.com/mamad8c/ComfyUI-H3-Latent-Upscaler-Mamad8.git
ARG H3_EXTENSIONS_BRANCH=main

# The 1.4.1 base DOES NOT contain /opt/comfyui-runtime-constraints.txt
# or .runpod-bundle-version. Generate our own torch constraints from the
# CUDA-13 wheel versions already installed in the image. We intentionally
# do NOT install a second PyTorch stack.
RUN python3.12 -c 'from importlib.metadata import version; print("".join(f"{p}=={version(p)}\n" for p in ("torch","torchvision","torchaudio")))' \
    > /opt/comfyui-runtime-constraints.txt

# Update /opt/comfyui-baked; RunPod's native /start.sh copies this seed to
# /workspace/runpod-slim/ComfyUI on FIRST BOOT (its v1.4.1 startup does not
# upgrade an existing workspace). A pre-existing workspace is guarded below.
RUN set -eux; \
    git -C /opt/comfyui-baked fetch --depth 1 origin "$COMFYUI_REF"; \
    git -C /opt/comfyui-baked checkout --force --detach FETCH_HEAD; \
    rm -rf /opt/comfyui-baked/custom_nodes/ComfyUI-Manager; \
    rm -rf /opt/comfyui-baked/custom_nodes/ComfyUI-RunpodDirect; \
    python3.12 -m pip install --no-cache-dir \
      -c /opt/comfyui-runtime-constraints.txt \
      --extra-index-url https://download.pytorch.org/whl/cu130 \
      -r /opt/comfyui-baked/requirements.txt; \
    python3.12 -m pip install --no-cache-dir \
      -c /opt/comfyui-runtime-constraints.txt \
      "comfyui_manager==$COMFYUI_MANAGER_VERSION"; \
    python3.12 -c 'import torch; assert torch.version.cuda and torch.version.cuda.startswith("13."), torch.version.cuda'; \
    git clone --depth 1 --branch "$PANEL_REF" "$PANEL_REPO" \
      /opt/comfyui-baked/custom_nodes/comfyui-mcp-panel; \
    git clone --depth 1 --single-branch --branch "$RUNPODDIRECT_BRANCH" "$RUNPODDIRECT_REPO" \
      /opt/comfyui-baked/custom_nodes/ComfyUI-RunpodDirect; \
    rm -rf /opt/comfyui-baked/custom_nodes/ComfyUI-MiniMaxH3-Context-Loop; \
    git clone --depth 1 --single-branch --branch "$H3_EXTENSIONS_BRANCH" "$H3_CONTEXT_LOOP_REPO" \
      /opt/comfyui-baked/custom_nodes/ComfyUI-MiniMaxH3-Context-Loop; \
    test "$(git -C /opt/comfyui-baked/custom_nodes/ComfyUI-MiniMaxH3-Context-Loop branch --show-current)" = "$H3_EXTENSIONS_BRANCH"; \
    test "$(git -C /opt/comfyui-baked/custom_nodes/ComfyUI-MiniMaxH3-Context-Loop rev-parse --abbrev-ref --symbolic-full-name '@{upstream}')" = "origin/$H3_EXTENSIONS_BRANCH"; \
    rm -rf /opt/comfyui-baked/custom_nodes/ComfyUI_MiniMax_H3_Extender; \
    git clone --depth 1 --single-branch --branch "$H3_EXTENSIONS_BRANCH" "$H3_EXTENDER_REPO" \
      /opt/comfyui-baked/custom_nodes/ComfyUI_MiniMax_H3_Extender; \
    test "$(git -C /opt/comfyui-baked/custom_nodes/ComfyUI_MiniMax_H3_Extender branch --show-current)" = "$H3_EXTENSIONS_BRANCH"; \
    test "$(git -C /opt/comfyui-baked/custom_nodes/ComfyUI_MiniMax_H3_Extender rev-parse --abbrev-ref --symbolic-full-name '@{upstream}')" = "origin/$H3_EXTENSIONS_BRANCH"; \
    rm -rf /opt/comfyui-baked/custom_nodes/ComfyUI-MiniMaxH3_LatentUpscaler; \
    git clone --depth 1 --single-branch --branch "$H3_EXTENSIONS_BRANCH" "$H3_LATENT_UPSCALER_REPO" \
      /opt/comfyui-baked/custom_nodes/ComfyUI-MiniMaxH3_LatentUpscaler; \
    test "$(git -C /opt/comfyui-baked/custom_nodes/ComfyUI-MiniMaxH3_LatentUpscaler branch --show-current)" = "$H3_EXTENSIONS_BRANCH"; \
    test "$(git -C /opt/comfyui-baked/custom_nodes/ComfyUI-MiniMaxH3_LatentUpscaler rev-parse --abbrev-ref --symbolic-full-name '@{upstream}')" = "origin/$H3_EXTENSIONS_BRANCH"; \
    rm -rf /opt/comfyui-baked/custom_nodes/ComfyUI-H3-Motion-Context-MultiRef; \
    git clone --depth 1 --single-branch --branch "$H3_EXTENSIONS_BRANCH" "$H3_MOTION_CONTEXT_REPO" \
      /opt/comfyui-baked/custom_nodes/ComfyUI-H3-Motion-Context-MultiRef; \
    test "$(git -C /opt/comfyui-baked/custom_nodes/ComfyUI-H3-Motion-Context-MultiRef branch --show-current)" = "$H3_EXTENSIONS_BRANCH"; \
    test "$(git -C /opt/comfyui-baked/custom_nodes/ComfyUI-H3-Motion-Context-MultiRef rev-parse --abbrev-ref --symbolic-full-name '@{upstream}')" = "origin/$H3_EXTENSIONS_BRANCH"; \
    rm -rf /opt/comfyui-baked/custom_nodes/ComfyUI-H3-Latent-Upscaler-Mamad8; \
    git clone --depth 1 --single-branch --branch "$H3_EXTENSIONS_BRANCH" "$H3_MAMAD8_UPSCALER_REPO" \
      /opt/comfyui-baked/custom_nodes/ComfyUI-H3-Latent-Upscaler-Mamad8; \
    test "$(git -C /opt/comfyui-baked/custom_nodes/ComfyUI-H3-Latent-Upscaler-Mamad8 branch --show-current)" = "$H3_EXTENSIONS_BRANCH"; \
    test "$(git -C /opt/comfyui-baked/custom_nodes/ComfyUI-H3-Latent-Upscaler-Mamad8 rev-parse --abbrev-ref --symbolic-full-name '@{upstream}')" = "origin/$H3_EXTENSIONS_BRANCH"; \
    test "$(git -C /opt/comfyui-baked/custom_nodes/ComfyUI-RunpodDirect branch --show-current)" = "$RUNPODDIRECT_BRANCH"; \
    test "$(git -C /opt/comfyui-baked/custom_nodes/ComfyUI-RunpodDirect rev-parse --abbrev-ref --symbolic-full-name '@{upstream}')" = "origin/$RUNPODDIRECT_BRANCH"; \
    if [ -f /opt/comfyui-baked/custom_nodes/comfyui-mcp-panel/requirements.txt ]; then \
      python3.12 -m pip install --no-cache-dir \
        -c /opt/comfyui-runtime-constraints.txt \
        --extra-index-url https://download.pytorch.org/whl/cu130 \
        -r /opt/comfyui-baked/custom_nodes/comfyui-mcp-panel/requirements.txt; \
    fi; \
    python3.12 -m pip install --no-cache-dir \
      -c /opt/comfyui-runtime-constraints.txt "aiohttp>=3.8.0"; \
    python3.12 -m pip install --no-cache-dir \
      -c /opt/comfyui-runtime-constraints.txt \
      -r /opt/comfyui-baked/custom_nodes/ComfyUI_MiniMax_H3_Extender/requirements.txt; \
    printf 'CUSTOM_COMFYUI_REF=%s\nCUSTOM_MANAGER_VERSION=%s\nCUSTOM_PANEL_REF=%s\nCUSTOM_RUNPODDIRECT_BRANCH=%s\n' \
      "$COMFYUI_REF" "$COMFYUI_MANAGER_VERSION" "$PANEL_REF" "$RUNPODDIRECT_BRANCH" \
      > /opt/comfyui-baked/.runpod-bundle-version

# Official Comfy-Org/comfy-mcp is a separate MCP server from artokun's
# Node.js agent; run it on demand via an authenticated SSH stdio session.
RUN python3.12 -m venv /opt/comfy-mcp-venv \
 && /opt/comfy-mcp-venv/bin/python -m pip install --no-cache-dir --upgrade pip \
 && /opt/comfy-mcp-venv/bin/python -m pip install --no-cache-dir \
      "comfy-cli>=1.14.0" comfy-mcp \
 && /opt/comfy-mcp-venv/bin/comfy --version \
 && /opt/comfy-mcp-venv/bin/comfy-mcp --version

# Strict startup patch for the PINNED RunPod 1.4.1 script, not the latest
# main branch (which has different variable and upgrade conventions).
COPY patch_base_start.py /opt/comfyui-fork/patch_base_start.py
RUN python3.12 /opt/comfyui-fork/patch_base_start.py /start.sh \
 && bash -n /start.sh

COPY official_comfy_mcp.sh /usr/local/bin/comfy-mcp-runpod
RUN chmod 755 /usr/local/bin/comfy-mcp-runpod \
 && bash -n /usr/local/bin/comfy-mcp-runpod \
 && test -s /opt/comfyui-baked/custom_nodes/comfyui-mcp-panel/__init__.py \
 && test -s /opt/comfyui-baked/custom_nodes/ComfyUI-RunpodDirect/__init__.py \
 && test -s /opt/comfyui-baked/custom_nodes/ComfyUI-MiniMaxH3-Context-Loop/__init__.py \
 && test -s /opt/comfyui-baked/custom_nodes/ComfyUI_MiniMax_H3_Extender/__init__.py \
 && test -s /opt/comfyui-baked/custom_nodes/ComfyUI-MiniMaxH3_LatentUpscaler/__init__.py \
 && test -s /opt/comfyui-baked/custom_nodes/ComfyUI-H3-Motion-Context-MultiRef/__init__.py \
 && test -s /opt/comfyui-baked/custom_nodes/ComfyUI-H3-Latent-Upscaler-Mamad8/__init__.py \
 && grep -qx 'CUSTOM_COMFYUI_REF=v0.42.1' /opt/comfyui-baked/.runpod-bundle-version

ENV COMFYUI_WORKSPACE=/workspace/runpod-slim/ComfyUI
EXPOSE 8188 22 8888 8080
# Inherit RunPod ENTRYPOINT ["/start.sh"]. No extra web UI, Jupyter or nginx.
