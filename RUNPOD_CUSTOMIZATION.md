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
| Model downloads | [ComfyUI-RunpodDirect](https://github.com/MadiatorLabs/ComfyUI-RunpodDirect), fresh tracked `main` clone baked into the image |
| Official MCP | [Comfy-Org/comfy-mcp](https://github.com/Comfy-Org/comfy-mcp), separate stdio integration |
| Artokun MCP | Existing Node.js application; normally runs on your PC |

## Persistent storage

The **pinned RunPod 1.4.1** `/start.sh` copies the image seed from `/opt/comfyui-baked`
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

### RunpodDirect Git branch tracking

The base RunPod image includes RunpodDirect, but its existing Git checkout may
lack an upstream branch. During a new image build, this fork replaces that
checkout with an explicit clone from `MadiatorLabs/ComfyUI-RunpodDirect` branch
`main` using `git clone --depth 1 --single-branch --branch main`. This sets
`main` to track `origin/main`, enabling ordinary `git pull --ff-only` updates.

**This only changes fresh first-boot workspaces.** An existing persistent
`/workspace/runpod-slim/ComfyUI/custom_nodes/ComfyUI-RunpodDirect` is kept
untouched; rebuilding the Docker image does not replace it. For such a Pod:

~~~bash
cd /workspace/runpod-slim/ComfyUI/custom_nodes/ComfyUI-RunpodDirect
set -e
git status --short
git fetch origin main
git switch main || git switch -c main --track origin/main
git branch --set-upstream-to=origin/main main
git pull --ff-only
~~~

Check and resolve uncommitted changes before switching; never discard them
with a forced reset. Restart the ComfyUI process, then hard-refresh the browser.

## H3 production nodes (optional alternatives)

The image includes Context Loop, H3 Extender, and H3 Latent Upscaler, plus the
Motion Context MultiRef dependency and Mamad8 upscaler architecture. The three
primary node packs are separate workflow options; do not wire multiple
production controllers into one sampling graph before testing compatibility.

Context Loop accepts imported Plan JSON via its Plan editor **JSON** button
or its `plan_json_input` STRING socket. Use
[Ref2V Studio](https://github.com/ethanfel/ComfyUI-MiniMaxH3-Context-Loop/tree/main/example_workflows)
for scene-specific `@tags` resolved to each shot's native Picture slots.
The JSON contains prompts and timing, **not image bytes**: import and register
actual images in ComfyUI's Project Asset Carousel. Use the Review Gate to
approve a scene before continuing.

On a fresh Pod, the extension checkouts are copied from the image's seed into
`/workspace/runpod-slim/ComfyUI/custom_nodes/`. Existing persistent
workspaces are **left untouched**; installing a newer Docker image won't
retrofit these nodes. On an existing Pod with a backed-up workspace:

~~~bash
cd /workspace/runpod-slim/ComfyUI/custom_nodes
git clone -b main https://github.com/seitanism/ComfyUI-H3-Motion-Context-MultiRef.git
git clone -b main https://github.com/ethanfel/ComfyUI-MiniMaxH3-Context-Loop.git
git clone -b main https://github.com/tritant/ComfyUI_MiniMax_H3_Extender.git
git clone -b main https://github.com/mamad8c/ComfyUI-H3-Latent-Upscaler-Mamad8.git
git clone -b main https://github.com/Tr1dae/ComfyUI-MiniMaxH3_LatentUpscaler.git
# Install Extender dependencies using your ComfyUI Python environment:
# /workspace/runpod-slim/ComfyUI/.venv-cu128/bin/python -m pip install -r ComfyUI_MiniMax_H3_Extender/requirements.txt
~~~

Skip any folders already installed, update or back them up instead of cloning over.
Restart ComfyUI and hard-refresh the browser. Verify new node names before a
full rendering run. Some H3 plugins patch the sampling pipeline and are
sensitive to the ComfyUI version. This change has not been GPU-tested.

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
python3 docker/runpod/validate_base_start.py
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

### Existing workspace compatibility

**RunPod image 1.4.1 does not automatically upgrade an existing workspace.**
The startup guard requires the image seed marker `CUSTOM_COMFYUI_REF=v0.42.1`.
If `/workspace/runpod-slim/ComfyUI` was populated by a previous pod/image,
startup stops with an explanatory error rather than silently launching an older
ComfyUI. Back up the volume and migrate the existing tree, or use a fresh volume
for the first deployment. **Do not delete a populated volume without a backup.**

The Dockerfile generates `/opt/comfyui-runtime-constraints.txt` and
`/opt/comfyui-baked/.runpod-bundle-version` because the pinned RunPod `1.4.1`
image does **not** supply them. The constraints preserve the base's CUDA 13
PyTorch wheel versions. Source validation against the exact pinned upstream
`start.sh` is provided by `docker/runpod/validate_base_start.py`.
