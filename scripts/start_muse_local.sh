#!/usr/bin/env bash
# Manual launch only. Requires llama.cpp >= b10353. Binds local HTTP only.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ "$#" -ne 1 ]]; then
  echo "Usage: bash scripts/start_muse_local.sh gpu|cpu" >&2
  exit 2
fi
MODE="$1"
if [[ "$MODE" != "gpu" && "$MODE" != "cpu" ]]; then
  echo "Expected gpu or cpu" >&2
  exit 2
fi
python -m scripts.muse_hardware_check
if [[ "$(printenv FRONTIERLAB_DOWNLOAD_OK || true)" != "YES" ]]; then
  echo "No model downloaded. 17GB download needs explicit FRONTIERLAB_DOWNLOAD_OK=YES." >&2
  exit 3
fi
if ! command -v llama-server >/dev/null 2>&1; then
  echo "Install llama.cpp b10353 or newer, with CUDA support for GPUs." >&2
  exit 4
fi
if [[ "$MODE" == "cpu" ]]; then
  exec llama-server -hf meta-models/Muse-Glimmer-30B-GGUF --hf-file Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf --no-mmproj -c 4096 -np 1 --host 127.0.0.1 --port 8080 --n-gpu-layers 0
fi
GPU_COUNT=$(nvidia-smi --query-gpu=index --format=csv,noheader | wc -l)
if [[ "$GPU_COUNT" -ge 2 ]]; then
  exec llama-server -hf meta-models/Muse-Glimmer-30B-GGUF --hf-file Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf --no-mmproj -c 4096 -np 1 --host 127.0.0.1 --port 8080 --split-mode layer --tensor-split 1,1 --n-gpu-layers 99
else
  exec llama-server -hf meta-models/Muse-Glimmer-30B-GGUF --hf-file Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf --no-mmproj -c 4096 -np 1 --host 127.0.0.1 --port 8080 --n-gpu-layers 99
fi
