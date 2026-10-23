#!/usr/bin/env python3
"""Fail-closed adaptations of the pinned official RunPod ComfyUI startup."""
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "/start.sh")
script = path.read_text()

def replace_once(old: str, new: str):
    global script
    occurrences = script.count(old)
    if occurrences != 1:
        raise RuntimeError(f"Unexpected RunPod start.sh structure: {old[:85]!r} ({occurrences} matches)")
    script = script.replace(old, new, 1)

# Missing token must NOT mean an unauthenticated Jupyter server.
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

# Stock FileBrowser has a publicly documented default password; opt in only
# when an explicit password is supplied (existing DB keeps its prior password).
replace_once("# Initialize FileBrowser if not already done", """if [[ -n "@@FILE@@" ]]; then
# Initialize FileBrowser if not already done""")
replace_once("nohup filebrowser &> /filebrowser.log &", """nohup filebrowser &> /filebrowser.log &
else
    echo "FileBrowser not launched: FILEBROWSER_PASSWORD not set"
fi""")

# Manager v4 comes from pip, so remove the historical classic Manager checkout.
replace_once(
    'BAKED_NODES=("ComfyUI-Manager" "ComfyUI-KJNodes" "Civicomfy" "ComfyUI-RunpodDirect")',
    'BAKED_NODES=("ComfyUI-KJNodes" "Civicomfy" "ComfyUI-RunpodDirect" "comfyui-mcp-panel")'
)
replace_once(
    'FIXED_ARGS="--listen 0.0.0.0 --port 8188 --enable-cors-header"',
    '''rm -rf "$COMFYUI_DIR/custom_nodes/ComfyUI-Manager"
FIXED_ARGS="--listen 0.0.0.0 --port 8188 --enable-cors-header --enable-manager"'''
)

# /workspace/ComfyUI alias: do not replace any existing user directory.
replace_once('cd $COMFYUI_DIR\n', '''if [[ ! -e /workspace/ComfyUI && ! -L /workspace/ComfyUI ]]; then
    ln -s "$COMFYUI_DIR" /workspace/ComfyUI
elif [[ -L /workspace/ComfyUI ]]; then
    ln -sfn "$COMFYUI_DIR" /workspace/ComfyUI
else
    echo "WARNING: /workspace/ComfyUI is a real directory; not overwriting"
fi
cd "$COMFYUI_DIR"
''')

script = script.replace("@@JUP@@", "$" + "{JUPYTER_PASSWORD:-}")
script = script.replace("@@FILE@@", "$" + "{FILEBROWSER_PASSWORD:-}")
path.write_text(script)
print("RunPod startup patched: Jupyter/FileBrowser gated, Manager v4, /workspace alias")
