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
    echo "converter stub: generate $EXT via dedicated skill/runtime" >&2
    exit 2
    ;;
  *)
    echo "unsupported extension: $EXT" >&2
    exit 3
    ;;
esac

echo "written: $OUT"
