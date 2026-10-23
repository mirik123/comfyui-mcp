#!/usr/bin/env bash
set -euo pipefail
echo "Upstream release disabled: this fork must not publish to artokun's Docker Hub/RunPod template." >&2
echo "Build and run docker/runpod/test_image.sh; then publish under your own namespace manually." >&2
exit 2
