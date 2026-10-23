#!/usr/bin/env python3
"""Patch the exact RunPod start.sh from runpod-workers/comfyui-base tag 1.4.1.
Fail closed on missing anchors rather than silently enabling public services.
"""
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "/start.sh")
script = path.read_text()

def replace_once(old: str, new: str):
    global script
    count = script.count(old)
    if count != 1:
        raise RuntimeError(f"Unsupported RunPod base startup: {old[:90]!r} ({count} matches)")
    script = script.replace(old, new, 1)

# The pinned base starts passwordless Jupyter unless this is explicitly gated.
replace_once("start_jupyter() {", """start_jupyter() {
    if [[ -z "@@JUP@@" ]]; then
        echo "JupyterLab disabled: JUPYTER_PASSWORD not set"
        return 0
    fi""")
replace_once("\nstart_jupyter\n", """
if [[ -n "@@JUP@@" ]]; then
    start_jupyter
else
    echo "JupyterLab not launched"
fi
""")

# The pinned base otherwise starts FileBrowser using a documented default
# password. Do not initialize it or bind port 8080 without an explicit password.
replace_once("# Initialize FileBrowser if not already done", """if [[ -n "@@FILE@@" ]]; then
# Initialize FileBrowser if not already done""")
replace_once("nohup filebrowser &> /filebrowser.log &", """nohup filebrowser &> /filebrowser.log &
else
    echo "FileBrowser not launched: FILEBROWSER_PASSWORD not set"
fi""")

# In version 1.4.1 this variable is a STRING, not the array in newer versions.
replace_once(
    'BAKED_NODES="ComfyUI-Manager ComfyUI-KJNodes Civicomfy ComfyUI-RunpodDirect"',
    'BAKED_NODES="ComfyUI-KJNodes Civicomfy ComfyUI-RunpodDirect comfyui-mcp-panel"',
)

# The 1.4.1 base has no automatic upgrade of /workspace/ComfyUI.
# Refuse to run an older ComfyUI copied by a previous pod, preserving its
# content. User can back up/migrate their old workspace or use a fresh volume.
replace_once(
    "# Warm up pip so ComfyUI-Manager's 5s timeout check doesn't fail on cold start",
    """EXPECTED_CORE=v0.42.1
if [[ ! -f "$COMFYUI_DIR/.runpod-bundle-version" ]] || ! grep -qx "CUSTOM_COMFYUI_REF=$EXPECTED_CORE" "$COMFYUI_DIR/.runpod-bundle-version"; then
    echo "ERROR: existing $COMFYUI_DIR is not this image's ComfyUI $EXPECTED_CORE."
    echo "Back up /workspace, migrate the existing ComfyUI tree, or deploy with an empty persistent volume."
    echo "Refusing to silently run a different ComfyUI version."
    exit 1
fi

# Warm up pip so ComfyUI-Manager's 5s timeout check doesn't fail on cold start""",
)

# Do not let the classic Manager custom node conflict with pip Manager v4.
replace_once(
    'FIXED_ARGS="--listen 0.0.0.0 --port 8188 --enable-cors-header"',
    '''rm -rf "$COMFYUI_DIR/custom_nodes/ComfyUI-Manager"
FIXED_ARGS="--listen 0.0.0.0 --port 8188 --enable-cors-header --enable-manager"''',
)

# Create an alias without clobbering user data. Actual install stays where
# RunPod's startup expects it, including the persistent Python environment.
replace_once('cd $COMFYUI_DIR\n', '''if [[ ! -e /workspace/ComfyUI && ! -L /workspace/ComfyUI ]]; then
    ln -s "$COMFYUI_DIR" /workspace/ComfyUI
elif [[ -L /workspace/ComfyUI ]]; then
    ln -sfn "$COMFYUI_DIR" /workspace/ComfyUI
else
    echo "WARNING: /workspace/ComfyUI is an existing directory; not overwriting it"
fi
cd "$COMFYUI_DIR"
''')

script = script.replace("@@JUP@@", "$" + "{JUPYTER_PASSWORD:-}")
script = script.replace("@@FILE@@", "$" + "{FILEBROWSER_PASSWORD:-}")
path.write_text(script)
print("Patched pinned RunPod 1.4.1 startup safely")
