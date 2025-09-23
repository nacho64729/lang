#!/usr/bin/env python3
"""
Combine PDFs named in the pattern: 第XX..._pageY.pdf
- XX is a Chinese numeral from 十一..二十 (11..20), at the START of the filename after '第'
- Y is an Arabic numeral at the END of the filename after '_page', before .pdf

Examples:
  第十一foo_page1.pdf
  第十二bar_page2.pdf
  第十三baz_page3.pdf
  ...
  第二十qux_page5.pdf

Usage:
  python combine_pdf_lessons.py /path/to/folder output.pdf
"""

import re
import sys
from pathlib import Path

# ---------- Import strategy ----------
USE_BACKEND = None
PdfWriter = None
PdfMergerFallback = None

try:
    from pypdf import PdfWriter
    USE_BACKEND = "pypdf-writer"
except Exception:
    try:
        from PyPDF2 import PdfMerger as PdfMergerFallback
        USE_BACKEND = "pypdf2-merger"
    except Exception:
        print(
            "Error: neither 'pypdf' (preferred) nor 'PyPDF2' (fallback) is installed.\n"
            "Install one of:\n"
            "  pip install pypdf\n"
            "  pip install PyPDF2",
            file=sys.stderr,
        )
        sys.exit(1)

# ---------- Numeral mapping & filename parsing ----------

CHINESE_NUM_MAP_11_20 = {
    "十一": 11, "十二": 12, "十三": 13, "十四": 14, "十五": 15,
    "十六": 16, "十七": 17, "十八": 18, "十九": 19, "二十": 20,
}

# Regex to match 第XX..._pageY.pdf, where XX is 十一..二十
FILENAME_RE = re.compile(
    r'^第(?P<x>(十一|十二|十三|十四|十五|十六|十七|十八|十九|二十)).*_page(?P<y>\d+)\.pdf$',
    re.IGNORECASE
)

def chinese_to_int_11_to_20(s: str) -> int:
    if s in CHINESE_NUM_MAP_11_20:
        return CHINESE_NUM_MAP_11_20[s]
    raise ValueError(f"Unsupported Chinese numeral for X (expect 十一..二十): {s}")

def find_and_sort_pdfs(folder: Path):
    items = []
    for entry in folder.iterdir():
        if not entry.is_file() or entry.suffix.lower() != ".pdf":
            continue
        m = FILENAME_RE.match(entry.name)
        if not m:
            print(f"Skipping (name pattern mismatch): {entry.name}")
            continue
        x_str = m.group("x")
        y_str = m.group("y")
        try:
            x_val = chinese_to_int_11_to_20(x_str)
        except ValueError as e:
            print(f"Skipping (unsupported X): {entry.name} -> {e}")
            continue
        y_val = int(y_str)
        items.append((x_val, y_val, entry))
    # Sort by X then Y
    items.sort(key=lambda t: (t[0], t[1]))
    return items

def combine_pdfs(sorted_items, output_path: Path):
    if not sorted_items:
        print("No matching PDFs found. Nothing to combine.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if USE_BACKEND == "pypdf-writer":
        writer = PdfWriter()
        try:
            for x_val, y_val, path in sorted_items:
                print(f"Appending: X={x_val:02d}, Y={y_val:03d}, file={path.name}")
                writer.append(str(path))
            writer.write(str(output_path))
            print(f"Combined PDF written to: {output_path}")
        finally:
            try:
                writer.close()
            except Exception:
                pass

    elif USE_BACKEND == "pypdf2-merger":
        merger = PdfMergerFallback()
        try:
            for x_val, y_val, path in sorted_items:
                print(f"Appending: X={x_val:02d}, Y={y_val:03d}, file={path.name}")
                merger.append(str(path))
            merger.write(str(output_path))
            print(f"Combined PDF written to: {output_path}")
        finally:
            try:
                merger.close()
            except Exception:
                pass

def main():
    if len(sys.argv) != 3:
        print("Usage: python combine_pdf_lessons.py /path/to/folder output.pdf", file=sys.stderr)
        sys.exit(2)

    folder = Path(sys.argv[1]).expanduser().resolve()
    output_path = Path(sys.argv[2]).expanduser().resolve()

    if not folder.exists() or not folder.is_dir():
        print(f"Error: folder not found or not a directory: {folder}", file=sys.stderr)
        sys.exit(3)

    items = find_and_sort_pdfs(folder)
    combine_pdfs(items, output_path)

if __name__ == "__main__":
    main()
