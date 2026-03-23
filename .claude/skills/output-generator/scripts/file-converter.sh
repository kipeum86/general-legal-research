#!/usr/bin/env bash
set -euo pipefail

# Minimal conversion dispatcher stub.
# Usage: file-converter.sh input.md output.ext

IN="${1:-}"
OUT="${2:-}"

if [[ -z "$IN" || -z "$OUT" ]]; then
  echo "usage: file-converter.sh <input> <output>" >&2
  exit 1
fi

EXT="${OUT##*.}"
case "$EXT" in
  md|txt|html)
    cp "$IN" "$OUT"
    ;;
  pdf|docx|pptx)
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    python3 "${SCRIPT_DIR}/file-converter.py" "$IN" "$OUT"
    ;;
  *)
    echo "unsupported extension: $EXT" >&2
    exit 3
    ;;
esac

echo "written: $OUT"
