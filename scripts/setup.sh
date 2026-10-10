#!/bin/zsh
# One-time setup for the khmer-history-doc skill (macOS, Apple Silicon recommended).
#   .venv      rendering: cairo, numpy, scipy, pillow, soundfile, pyloudnorm, pyshp
#   .venv-vox  voices + ASR check: VoxCPM2 (PyTorch/MPS) + transformers (Khmer Whisper)
# Re-running is safe.  Set SKIP_VOX=1 to skip the voice environment.
set -e
SK="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3.12}"
command -v "$PY" >/dev/null || PY=python3
echo "skill: $SK   python: $($PY --version)"

echo "1/4 system tools (Homebrew)"
for pkg in ffmpeg cairo pango; do
  brew list "$pkg" >/dev/null 2>&1 || brew install "$pkg"
done

echo "2/4 fonts"
fc-list | grep -q "Noto Sans Khmer" || brew install --cask font-noto-sans-khmer
fc-list | grep -q "Noto Serif Khmer" || brew install --cask font-noto-serif-khmer
fc-list | grep -q "Moul" || brew install --cask font-moul
fc-list | grep -q "Cormorant Garamond" || brew install --cask font-cormorant-garamond

echo "3/4 render environment (.venv)"
[ -x "$SK/.venv/bin/python" ] || "$PY" -m venv "$SK/.venv"
"$SK/.venv/bin/pip" install -q --upgrade pip
"$SK/.venv/bin/pip" install -q -r "$SK/requirements.txt"

echo "4/4 voice environment (.venv-vox)"
if [ -n "$SKIP_VOX" ]; then
  echo "  skipped (SKIP_VOX=1)"
elif [ -x "$HOME/.claude/skills/khmer-2d-animation/.venv-vox/bin/python" ] && [ ! -e "$SK/.venv-vox" ]; then
  ln -s "$HOME/.claude/skills/khmer-2d-animation/.venv-vox" "$SK/.venv-vox"
  "$SK/.venv-vox/bin/pip" install -q transformers scipy
  echo "  reusing khmer-2d-animation's .venv-vox"
else
  [ -x "$SK/.venv-vox/bin/python" ] || "$PY" -m venv "$SK/.venv-vox"
  "$SK/.venv-vox/bin/pip" install -q --upgrade pip
  "$SK/.venv-vox/bin/pip" install -q -r "$SK/requirements-vox.txt"
fi
if [ -z "$SKIP_VOX" ]; then
  "$SK/.venv-vox/bin/python" -c "import voxcpm, torch; print('  torch', torch.__version__, 'mps', torch.backends.mps.is_available())"
  echo "  downloading VoxCPM2 (~5 GB, first time only)"
  "$SK/.venv-vox/bin/python" -c "from huggingface_hub import snapshot_download; print('  model:', snapshot_download('openbmb/VoxCPM2'))"
fi
echo "done.  New film:  $SK/.venv/bin/python $SK/scripts/new_doc.py ~/animation-2D/<name> --title-en '...' --title-km '...'"
