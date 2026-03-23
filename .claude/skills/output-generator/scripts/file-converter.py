"""
File converter with bidirectional support:
- INPUT:  PDF/DOCX/PPTX → Markdown (using markitdown)
- OUTPUT: Markdown → target format (delegates to render scripts)
- PASSTHROUGH: md/txt/html → copy

Usage: python3 file-converter.py <input> <output>
Dependencies: pip install 'markitdown[pdf,docx]'
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

MARKITDOWN_INPUT_EXTS = {".pdf", ".docx", ".pptx", ".xlsx"}
PASSTHROUGH_EXTS = {".md", ".txt", ".html"}


def _ensure_markitdown():
    try:
        from markitdown import MarkItDown
        return MarkItDown()
    except ImportError:
        print(
            "ERROR: markitdown is not installed.\n"
            "Run:  pip install 'markitdown[pdf,docx]'\n"
            "Or with venv:  source .venv/bin/activate && pip install 'markitdown[pdf,docx]'",
            file=sys.stderr,
        )
        sys.exit(1)


def convert(input_path: Path, output_path: Path) -> None:
    in_ext = input_path.suffix.lower()
    out_ext = output_path.suffix.lower()

    # Case 1: Binary → Markdown/text (input conversion via markitdown)
    if in_ext in MARKITDOWN_INPUT_EXTS and out_ext in {".md", ".txt"}:
        md = _ensure_markitdown()
        result = md.convert(str(input_path))
        text = result.text_content or ""
        if len(text.strip()) < 50:
            print(
                f"WARNING: Extracted text is very short ({len(text.strip())} chars). "
                "Source may be scanned/image-only.",
                file=sys.stderr,
            )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
        print(f"converted: {input_path} → {output_path}")
        return

    # Case 2: Passthrough (same-family copy)
    if in_ext in PASSTHROUGH_EXTS and out_ext in PASSTHROUGH_EXTS:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(input_path), str(output_path))
        print(f"copied: {input_path} → {output_path}")
        return

    # Case 3: Markdown → Binary (output generation — delegate to render scripts)
    if in_ext in PASSTHROUGH_EXTS and out_ext in MARKITDOWN_INPUT_EXTS:
        print(
            f"converter: {out_ext} output generation requires a dedicated render script.\n"
            f"For DOCX: use scripts/render_professional_legal_opinion_docx.py\n"
            f"For other formats: use the output-generator skill.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Case 4: Unsupported
    print(f"unsupported conversion: {in_ext} → {out_ext}", file=sys.stderr)
    sys.exit(3)


def main() -> None:
    if len(sys.argv) != 3:
        print("usage: file-converter.py <input> <output>", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    convert(input_path, output_path)


if __name__ == "__main__":
    main()
