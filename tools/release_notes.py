r"""Print the release notes for a tag from HANDOVER.md's 릴리즈 기록 list.

Usage: python tools/release_notes.py v0.14.1 [--out notes.md]
Used by .github/workflows/release.yml; falls back to a generic note when the tag
has no entry so a release is never blocked by documentation.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FALLBACK = "Download ChroniclesOfPixel.exe from the assets below and double click it to play."
DOWNLOAD = "아래 Assets의 **ChroniclesOfPixel.exe**를 내려받아 더블 클릭하면 바로 실행됩니다."


def notes_for(tag, handover_text):
    pattern = re.compile(r"^- \*\*" + re.escape(tag) + r":\*\*\s*(.+)$", re.MULTILINE)
    match = pattern.search(handover_text)
    if not match:
        return FALLBACK
    return f"## {tag}\n\n{match.group(1).strip()}\n\n{DOWNLOAD}\n"


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    tag = argv[0]
    text = (ROOT / "HANDOVER.md").read_text(encoding="utf-8")
    notes = notes_for(tag, text)
    if "--out" in argv:
        Path(argv[argv.index("--out") + 1]).write_text(notes, encoding="utf-8")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(notes)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
