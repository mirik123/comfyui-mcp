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
| Server-side model downloads | [MadiatorLabs/ComfyUI-RunpodDirect](https://github.com/MadiatorLabs/ComfyUI-RunpodDirect), cloned from tracked `main` during the image build |
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

### H3 long-form production toolkits

The image now includes three alternative H3 tools:

- [Context Loop](https://github.com/ethanfel/ComfyUI-MiniMaxH3-Context-Loop): import Plan JSON (Plan's **JSON** button or `plan_json_input`), per-shot prompts, tagged scene references, review/retry and checkpoint/resume.
- [H3 Extender](https://github.com/tritant/ComfyUI_MiniMax_H3_Extender): clip cards, per-clip references, Full Batch, project persistence.
- [H3 Latent Upscaler](https://github.com/Tr1dae/ComfyUI-MiniMaxH3_LatentUpscaler): optional two-pass 2× latent spatial refinement; not an automatic improvement in visual quality.

The image also installs Context Loop's documented [Motion Context MultiRef](https://github.com/seitanism/ComfyUI-H3-Motion-Context-MultiRef) dependency and the upscaler's [Mamad8 architecture pack](https://github.com/mamad8c/ComfyUI-H3-Latent-Upscaler-Mamad8). Each checkout follows its `main` branch, with an upstream configured for `git pull --ff-only`. H3 model weights and upscaler weights are **not baked into the image**; the upscaler's learned checkpoint may download when first used.

**RunPod persistent-volume behavior:** Existing `/workspace/runpod-slim/ComfyUI` contents are not updated by a new image. Install these nodes manually on an existing Pod or migrate to a fresh ComfyUI workspace after backing up. Do not delete your existing models and project data. Avoid mixing the three long-form controllers inside the **same graph** without testing; they are alternatives, not one mandatory combined workflow. GPU inference/coexistence have not been verified.


### RunpodDirect updates

The Docker build replaces the RunPod base image's existing `ComfyUI-RunpodDirect` checkout with an explicit clone of the extension's `main` branch, tracking `origin/main`. This makes `git pull --ff-only` work in new installations. After first boot the extension lives on the persistent `/workspace` volume, and **rebuilding the image does not update an existing volume**.

To repair a previously installed checkout on an existing Pod without deleting its data:

~~~bash
cd /workspace/runpod-slim/ComfyUI/custom_nodes/ComfyUI-RunpodDirect
set -e
git status --short               # inspect and preserve any local changes
git fetch origin main
git switch main || git switch -c main --track origin/main
git branch --set-upstream-to=origin/main main
git pull --ff-only
~~~

If Git reports uncommitted changes or diverging history, resolve them before switching or pulling; do not force-reset your working copy. Restart ComfyUI and hard-refresh the browser after updating the extension. See [RunPod customization](RUNPOD_CUSTOMIZATION.md) for persistent-volume considerations.

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
- **RunpodDirect:** [MadiatorLabs/ComfyUI-RunpodDirect](https://github.com/MadiatorLabs/ComfyUI-RunpodDirect), GPL-3.0 licensed, installed as a separate third-party ComfyUI extension.

Third-party components retain their own licenses and attribution requirements. This fork's changes do not imply endorsement by the upstream maintainers.
