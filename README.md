# ComfyUI MCP — RunPod CUDA 13 Fork

A RunPod-focused fork of [artokun/comfyui-mcp](https://github.com/artokun/comfyui-mcp) **v0.52.206**. This fork restores the upstream Docker infrastructure from **v0.52.203** and provides a custom image for ComfyUI, AI-assisted workflow editing, and MCP integration on a RunPod GPU.

This is a community fork, **not an official release** of artokun's project, Comfy-Org, or RunPod.

## What this fork changes

| Component | Configuration |
| --- | --- |
| Base image | `runpod/comfyui:1.4.1-cuda13.0` |
| ComfyUI | `v0.42.1` |
| GPU runtime | CUDA 13.0; reuse PyTorch from the RunPod image |
| ComfyUI Manager | `comfyui_manager==4.2.2`, enabled using `--enable-manager` |
| Agent sidebar | [artokun/comfyui-mcp-panel](https://github.com/artokun/comfyui-mcp-panel) |
| Official MCP server | [Comfy-Org/comfy-mcp](https://github.com/Comfy-Org/comfy-mcp), isolated Python environment |
| Artokun MCP agent | Existing Node.js agent from upstream v0.52.206; usually runs on your own PC |
| Persistent ComfyUI | `/workspace/runpod-slim/ComfyUI` |
| Convenience path | `/workspace/ComfyUI` symlink |
| JupyterLab | Starts **only** when `JUPYTER_PASSWORD` is nonempty |
| FileBrowser | Starts **only** when `FILEBROWSER_PASSWORD` is nonempty |
| code-server | Not installed |
| Web UI | Port `8188`; no extra nginx proxy on 3000 |

The Dockerfile modifies the **image-baked ComfyUI seed** at `/opt/comfyui-baked`. RunPod's original startup copies that seed into the persistent workspace on first boot and starts ComfyUI from there. The official MCP server runs separately through stdio and does **not** open another public service.

## Build

From the repository root:

~~~bash
python3 docker/runpod/validate_sources.py
python3 docker/runpod/validate_base_start.py

docker build -t mirik123/comfyui-mcp-runpod:comfy042-cu130 docker/runpod

bash docker/runpod/test_image.sh mirik123/comfyui-mcp-runpod:comfy042-cu130
~~~

The Docker build and smoke tests can also run through [GitHub Actions](.github/workflows/build-runpod-image.yml). The workflow builds and checks the image without publishing it. No Docker Hub image or RunPod template is automatically updated.

**Testing status:** The startup changes have been reviewed against RunPod's pinned `1.4.1` source. A successful full Docker build, RunPod GPU startup, and LTX video render have **not** been verified. Run the CI checks and a GPU test before deploying this image for production work.

## RunPod deployment

Build and push the image to a registry you control, then deploy it using a RunPod Pod with a **persistent volume mounted at `/workspace`**. Select a CUDA 13-compatible NVIDIA host driver (typically R580 or newer).

The persistent installation contains ComfyUI, custom nodes, a Python virtual environment, inputs, outputs, models and user configuration. The virtual environment may retain RunPod's historical name `.venv-cu128` even though the base image uses CUDA 13.

**Existing volume warning:** The pinned RunPod `1.4.1` startup does not upgrade an existing ComfyUI checkout automatically. This fork checks a version marker and refuses to launch an incompatible existing workspace. Back up and migrate the old installation, or use a fresh persistent volume. Do not delete a populated volume without a backup.

LTX model files and other model weights are **not bundled**.

### Access and security

| Service | Port | Requirement |
| --- | --- | --- |
| ComfyUI + Agent Panel | 8188 | Protect access to the pod |
| SSH | 22 | Configure `PUBLIC_KEY` |
| JupyterLab | 8888 | Set `JUPYTER_PASSWORD` |
| FileBrowser | 8080 | Set `FILEBROWSER_PASSWORD` |
| Official Comfy MCP | stdio | Invoke through authenticated SSH |

Do not expose ComfyUI Manager or its API to untrusted users. On a reused workspace, an existing FileBrowser database retains its stored credentials; the environment variable alone does not reset an existing password.

## Connecting an AI agent

### Artokun Agent Panel — from your Windows PC

With Node.js 22+ and Codex installed and authenticated:

~~~powershell
codex login
npx -y comfyui-mcp@0.52.206 connect https://YOUR-POD-ID-8188.proxy.runpod.net
~~~

Open ComfyUI in your browser, select the **Agent** sidebar, and click **Connect**. The orchestrator uses your local subscription/login rather than installing an agent runtime in the GPU container.

### Official Comfy MCP — over SSH

The Docker image separately installs the official MCP server into `/opt/comfy-mcp-venv`. Configure an MCP client to execute:

~~~bash
ssh -T root@YOUR_RUNPOD_SSH_ENDPOINT /usr/local/bin/comfy-mcp-runpod
~~~

Use the SSH endpoint and port supplied by RunPod. The wrapper selects the installed ComfyUI workspace, then launches the MCP server over standard input/output.

See [RunPod customization and validation](RUNPOD_CUSTOMIZATION.md) and [the active Dockerfile](docker/runpod/Dockerfile) for details. Other restored Docker scripts are retained for provenance; upstream release/publishing scripts are deliberately disabled so they cannot publish to artokun's accounts.

## Attribution and licenses

- **Original comfyui-mcp:** Created by **Arthur R. Longbottom ([@artokun](https://github.com/artokun))** — [original repository](https://github.com/artokun/comfyui-mcp), MIT licensed. The original copyright notice and license terms are preserved in [LICENSE](LICENSE).
- **ComfyUI Agent Panel:** [artokun/comfyui-mcp-panel](https://github.com/artokun/comfyui-mcp-panel), maintained separately from this fork.
- **ComfyUI:** [Comfy-Org / ComfyUI](https://github.com/comfyanonymous/ComfyUI) and contributors.
- **Official Comfy MCP:** [Comfy-Org/comfy-mcp](https://github.com/Comfy-Org/comfy-mcp).
- **RunPod ComfyUI base:** [runpod-workers/comfyui-base](https://github.com/runpod-workers/comfyui-base) and the `runpod/comfyui` Docker image.

Third-party components retain their own licenses and attribution requirements. This fork's changes do not imply endorsement by the upstream maintainers.
