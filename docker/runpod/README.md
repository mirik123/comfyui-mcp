# RunPod CUDA 13 — ComfyUI 0.42.1 + two MCP integrations

This is the **active RunPod deployment** for the fork of artokun/comfyui-mcp
**v0.52.206**. The original `docker/` sources, Dockerfile, release scripts
and GitHub workflow have been restored from upstream **v0.52.203**, but the
active image has been redesigned around RunPod's official ComfyUI base.

| Component | Version or role |
| --- | --- |
| Base | `runpod/comfyui:1.4.1-cuda13.0` |
| Core | ComfyUI `v0.42.1` |
| CUDA / Torch | CUDA 13.0 and base-supplied PyTorch; no duplicate Torch install |
| Manager | pip `comfyui_manager==4.2.2`, `--enable-manager` |
| Sidebar | [artokun/comfyui-mcp-panel](https://github.com/artokun/comfyui-mcp-panel) |
| Official MCP | [Comfy-Org/comfy-mcp](https://github.com/Comfy-Org/comfy-mcp), separate stdio integration |
| Artokun MCP | Existing Node.js application; normally runs on your PC |

## Persistent storage

The official RunPod `/start.sh` copies the image seed from `/opt/comfyui-baked`
into **`/workspace/runpod-slim/ComfyUI`** and creates the persistent Python
environment there on first boot. This image also creates
`/workspace/ComfyUI` as a symlink to the same directory.

Use a RunPod network volume mounted at `/workspace`. Your installed custom
nodes, Python environment, models, inputs, outputs and settings then persist
across pod restarts. Some models may use additional paths according to your
workflow and node configuration. The virtualenv may still be named
`.venv-cu128` by the official RunPod script: this is just its historic name,
not the system CUDA version.

The official MCP environment at `/opt/comfy-mcp-venv` is baked in the Docker
image, and is rebuilt when the image is rebuilt. It is not a second ComfyUI.

## Services

| Service | Port | Behavior |
| --- | --- | --- |
| ComfyUI + artokun sidebar | 8188 | Always starts |
| SSH | 22 | Configure a `PUBLIC_KEY` |
| JupyterLab | 8888 | **Only if JUPYTER_PASSWORD is set** |
| FileBrowser | 8080 | **Only if FILEBROWSER_PASSWORD is set** |
| code-server | — | Not installed |
| Official Comfy MCP | stdio | Invoke on demand over authenticated SSH |

The FileBrowser password env variable is for initial database creation:
a previously created database keeps its old password until it is changed.
Avoid exposing the ComfyUI API or Manager to untrusted users.

## Build and smoke tests

From the repository root:

~~~bash
python3 docker/runpod/validate_sources.py
docker build -t mirik123/comfyui-mcp-runpod:comfy042-cu130 docker/runpod
bash docker/runpod/test_image.sh mirik123/comfyui-mcp-runpod:comfy042-cu130
~~~

The GitHub Actions workflow can be triggered manually and **will not
publish** the image. Before deploying, test on a real RunPod GPU with a
CUDA-13-compatible host driver (typically R580+). Run a generation and
restart to check that nodes and their dependencies remain installed.

The image does **not** bundle LTX-2.5 model weights.

## Connect agents

Artokun's Agent Panel is installed in the ComfyUI sidebar, but its Node.js
orchestrator is normally started on your Windows PC (Node.js 22+ and Codex
signed in). Run:

~~~powershell
npx -y comfyui-mcp@latest connect https://YOUR-POD-ID-8188.proxy.runpod.net
~~~

Then click **Connect** in the Agent sidebar. Artokun's backend is not the same
as the official Comfy MCP.

For the official Comfy MCP, configure a client to run the following stdio
command over an authenticated SSH connection to your pod:

~~~bash
ssh -T root@YOUR_RUNPOD_SSH_ENDPOINT /usr/local/bin/comfy-mcp-runpod
~~~

The wrapper selects the existing ComfyUI path via `comfy set-default` and
executes official `comfy-mcp`. No extra public MCP port is opened.

## Legacy material and limitations

Historical `docker/runpod/post_start.sh`, nginx :3000→:3001, the old
`docker/compose` and `docker/trainer` are retained for provenance only.
The new image inherits the official RunPod startup and uses port 8188.

Original publishing scripts targeted artokun's Docker Hub and RunPod template.
They are **disabled** to prevent an accidental upstream publication.
The build-time startup patch is deliberately fail-closed: if RunPod changes
an expected startup-script anchor, the build stops instead of possibly
opening unauthenticated JupyterLab.

Static repository checks do not validate Docker runtime or CUDA kernels.
The GitHub editing environment has no Docker daemon or GPU; real image build
and LTX generation are not yet tested.
