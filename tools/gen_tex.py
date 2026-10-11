#!/usr/bin/env python3
"""Generate a LaTeX source for the Bhagavad Gita from the slok/ and chapter/ JSON files.

Layout per verse (landscape): Sanskrit | Transliteration (IAST) | English | Notes
"""
import argparse
import json
import re
from pathlib import Path

TRANSLATORS = {
    "siva": "Swami Sivananda",
    "purohit": "Shri Purohit Swami",
    "gambir": "Swami Gambirananda",
    "adi": "Swami Adidevananda",
    "san": "Dr. S. Sankaranarayan",
    "prabhu": "A.C. Bhaktivedanta Swami Prabhupada",
}
FALLBACK_ORDER = ["siva", "purohit", "gambir", "adi", "san", "prabhu"]

_ESC = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def esc(s: str) -> str:
    return "".join(_ESC.get(c, c) for c in s)


def lines(s: str) -> str:
    """Join the lines of a verse with forced line breaks inside a table cell."""
    parts = [esc(p.strip()) for p in s.strip().splitlines() if p.strip()]
    return r"\newline ".join(parts)


_VERSE_PREFIX = re.compile(r"^\s*\d+\.\d+\.?\s*")


def english(verse: dict, translator: str) -> str:
    order = [translator] + [t for t in FALLBACK_ORDER if t != translator]
    for key in order:
        entry = verse.get(key)
        if isinstance(entry, dict) and entry.get("et"):
            text = _VERSE_PREFIX.sub("", entry["et"].strip())
            return esc(text)
    return ""


def load_chapters(root: Path):
    chapters = []
    for f in sorted(root.glob("chapter/*.json"), key=lambda p: int(re.search(r"_(\d+)\.json$", p.name).group(1))):
        chapters.append(json.loads(f.read_text(encoding="utf-8")))
    return chapters


def load_verses(root: Path, chapter: int):
    files = root.glob(f"slok/bhagavadgita_chapter_{chapter}_slok_*.json")
    verses = [json.loads(f.read_text(encoding="utf-8")) for f in files]
    verses.sort(key=lambda v: int(v["verse"]))
    return verses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."), help="repository root")
    ap.add_argument("--translator", default="siva", choices=sorted(TRANSLATORS))
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    out = []
    w = out.append
    w(r"\input{preamble}")
    w(r"\newcommand{\translatorname}{%s}" % esc(TRANSLATORS[args.translator]))
    w(r"\begin{document}")
    w(r"\input{titlepage}")
    w(r"\tableofcontents")
    w(r"\clearpage")

    for ch in load_chapters(args.root):
        n = int(ch["chapter_number"])
        w(r"\chapter{%s}{%s}{%s}{%s}" % (
            n, esc(ch["name"]), esc(ch["transliteration"]), esc(ch["meaning"]["en"])))
        if ch.get("summary", {}).get("en"):
            w(r"\chaptersummary{%s}" % esc(ch["summary"]["en"]))
        w(r"\begin{tabularx}{\textwidth}{"
          r">{\RaggedRight\arraybackslash}p{0.23\textwidth}"
          r">{\RaggedRight\arraybackslash}p{0.21\textwidth}"
          r">{\RaggedRight\arraybackslash}X"
          r">{\RaggedRight\arraybackslash}p{0.22\textwidth}}")
        w(r"\versehead")
        last_speaker = None
        for v in load_verses(args.root, n):
            speaker = v.get("speaker") or ""
            cell = ""
            if speaker and speaker != last_speaker:
                cell += r"\speaker{%s}\newline " % esc(speaker)
                last_speaker = speaker
            cell += lines(v["slok"])
            w(r"\verseno{%d.%d}" % (n, int(v["verse"])))
            w("  {\\sanskrit %s}" % cell)
            w("  & {\\iast %s}" % lines(v["transliteration"]))
            w("  & %s" % english(v, args.translator))
            w("  & \\\\")
            w(r"\verserule")
        w(r"\end{tabularx}")

    w(r"\end{document}")
    args.output.write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
