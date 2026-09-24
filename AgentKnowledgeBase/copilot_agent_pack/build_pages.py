"""Build the GitHub Pages site in /docs from the agent knowledge files.

The site exists so a Microsoft 365 Copilot agent can use it as "public website"
knowledge. That knowledge type accepts URLs at most two levels deep and only
sees what Bing has indexed, so:
  - every page sits directly in docs/ (site root .../TestLab/ is 1 level,
    pages are 2 levels) - never add subfolders;
  - pages are plain server-rendered HTML with no JavaScript, so Bing indexes
    the full text;
  - the text of every knowledge file is reproduced exactly (inside <pre>), with
    section headings lifted out only to give search results useful anchors.

Re-run after changing anything in knowledge/:
    python AgentKnowledgeBase/copilot_agent_pack/build_pages.py
"""

from __future__ import annotations

import datetime as dt
import html
import re
import shutil
from pathlib import Path

import markdown

PACK = Path(__file__).resolve().parent
KNOWLEDGE = PACK / "knowledge"
REPO = PACK.parent.parent
DOCS = REPO / "docs"
SITE = "https://jaramillo35.github.io/TestLab/"
INDEXNOW_KEY = "7f3c9e2a4b8d41f6a0c5e9b2d7f14a38"

BAR = re.compile(r"^={5,}\s*$")
SUBSECTION = re.compile(r"^\d+\.\d+ [A-Z]")      # "4.1 ALLOWLIST ..." at column 0
CAPS_HEADING = re.compile(r"^[A-Z][A-Z0-9 ,&'()/-]{3,}$")  # "WHAT THE PROJECT IS"

PAGES = [
    # (output, source, title, description, kind)
    ("spec.html", "01_DISCOVERY_TOOL_SPEC.txt",
     "Discovery tool specification",
     "Self-contained specification for the read-only discovery tool: rules, "
     "command allowlists for the B&K 2831E and DAQ3120, output, tests, delivery format.",
     "text"),
    ("operator.html", "02_OPERATOR_SETUP_AND_SESSIONS.txt",
     "Operator setup and discovery sessions",
     "Bench preparation for the B&K 2831E multimeters and DAQ3120, front-panel "
     "settings, session plan S1-S7 and stop conditions.",
     "text"),
    ("commands.html", "03_COMMAND_REFERENCE_2831E_DAQ3120.txt",
     "Command reference - B&K 2831E and DAQ3120",
     "Manufacturer-manual-cited SCPI command reference for the B&K 2831E and "
     "DAQ3120 only, with page citations and known documentation gaps.",
     "markdown"),
    ("context.html", "06_PROJECT_CONTEXT.txt",
     "Project context",
     "Why the discovery tool exists, decisions already made, open questions it "
     "answers, and the safety principles of the project.",
     "text"),
    ("profiles.html", "07_INSTRUMENT_PROFILES_2831E_DAQ3120.txt",
     "Instrument profiles - B&K 2831E and DAQ3120",
     "Capabilities, transports, USB identifiers, DAQ3120 module catalogue and "
     "digital I/O pinout, in YAML form.",
     "pre"),
]

PDFS = [
    ("bk-2831e-manual.pdf", "04_BK_2831E_user_and_programming_manual.pdf",
     "B&K 2831E user and programming manual (71 pages)"),
    ("daq3120-programming-manual.pdf", "05_BK_DAQ3120_programming_manual.pdf",
     "B&K DAQ3120 programming manual (139 pages)"),
]

CSS = """
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:60rem;
margin:0 auto;padding:1.5rem;line-height:1.5;color:#1b1b1b;background:#fff}
h1{font-size:1.6rem;margin:.2rem 0 .8rem}
h2{font-size:1.2rem;margin:2rem 0 .4rem;padding-top:.6rem;border-top:1px solid #ddd}
h3{font-size:1.05rem;margin:1.4rem 0 .3rem}
pre{white-space:pre-wrap;word-wrap:break-word;background:#f6f7f8;padding:.8rem 1rem;
border-radius:6px;font-size:.9rem;line-height:1.4;margin:.4rem 0}
table{border-collapse:collapse;font-size:.9rem;margin:.6rem 0;display:block;overflow-x:auto}
th,td{border:1px solid #ccc;padding:.3rem .5rem;vertical-align:top;text-align:left}
code{font-size:.9em}
.note{background:#fff8e1;border-left:4px solid #e0a800;padding:.6rem .9rem;margin:1rem 0}
nav{font-size:.9rem;margin-bottom:1rem}
footer{margin-top:3rem;font-size:.85rem;color:#555;border-top:1px solid #ddd;padding-top:.8rem}
"""


def page(title: str, description: str, body: str, today: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} - Vehicle Harness Functional Tester</title>
<meta name="description" content="{html.escape(description)}">
<style>{CSS}</style>
</head>
<body>
<nav><a href="./">Vehicle Harness Functional Tester - discovery tool knowledge</a></nav>
{body}
<footer>Vehicle Harness Functional Tester &middot; updated {today} &middot;
Source: github.com/Jaramillo35/TestLab, AgentKnowledgeBase/copilot_agent_pack/knowledge.
Commands shown here are transcribed from manufacturer manuals and are NOT approved for
hardware execution. The discovery tool may send only the allowlisted strings in the
specification.</footer>
</body>
</html>
"""


def text_to_html(text: str) -> str:
    """Exact text in <pre> blocks; headings lifted out as <h2>/<h3>."""
    lines = text.splitlines()
    out: list[str] = [f"<h1>{html.escape(lines[0])}</h1>"]
    buf: list[str] = []

    def flush() -> None:
        while buf and not buf[0].strip():
            buf.pop(0)
        while buf and not buf[-1].strip():
            buf.pop()
        if buf:
            out.append("<pre>" + html.escape("\n".join(buf)) + "</pre>")
        buf.clear()

    i = 1
    while i < len(lines):
        line = lines[i]
        if BAR.match(line) and i + 2 < len(lines) and BAR.match(lines[i + 2]):
            flush()
            out.append(f"<h2>{html.escape(lines[i + 1].strip())}</h2>")
            i += 3
            continue
        if SUBSECTION.match(line):
            flush()
            out.append(f"<h3>{html.escape(line.strip())}</h3>")
        elif CAPS_HEADING.match(line) and not line.startswith(" "):
            flush()
            out.append(f"<h2>{html.escape(line.strip())}</h2>")
        else:
            buf.append(line)
        i += 1
    flush()
    return "\n".join(out)


def build() -> None:
    today = dt.date.today().isoformat()
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()

    for out_name, src, title, desc, kind in PAGES:
        raw = (KNOWLEDGE / src).read_text(encoding="utf-8")
        if kind == "text":
            body = text_to_html(raw)
        elif kind == "markdown":
            preamble, _, md_body = raw.partition("=" * 78 + "\n")
            body = (f"<h1>{html.escape(title)}</h1>"
                    f"<div class=note><pre>{html.escape(preamble.strip())}</pre></div>"
                    + markdown.markdown(md_body, extensions=["tables", "fenced_code"]))
        else:  # pre
            body = f"<h1>{html.escape(title)}</h1><pre>{html.escape(raw)}</pre>"
        (DOCS / out_name).write_text(page(title, desc, body, today), encoding="utf-8")

    for out_name, src, _ in PDFS:
        shutil.copyfile(KNOWLEDGE / src, DOCS / out_name)

    items = "\n".join(
        f'<li><a href="{o}">{html.escape(t)}</a> - {html.escape(d)}</li>'
        for o, _, t, d, _ in PAGES)
    pdfs = "\n".join(f'<li><a href="{o}">{html.escape(t)}</a></li>' for o, _, t in PDFS)
    index_body = f"""<h1>Vehicle Harness Functional Tester - discovery tool knowledge</h1>
<p>Knowledge for building and running a read-only Python discovery tool for two
bench instruments: the <strong>B&amp;K Precision 2831E</strong> multimeter and the
<strong>B&amp;K Precision DAQ3120</strong> data acquisition system. The tool connects
to one instrument at a time, asks read-only questions, and records the answers
needed to build the test application's GUI and drivers.</p>
<div class=note><strong>Start with the specification.</strong> It is the authoritative
document and wins over every other page. The tool may send only the exact command
strings in its allowlists. The oscilloscope and power supply are out of scope and are
deliberately not covered here.</div>
<h2>Pages</h2>
<ul>
{items}
</ul>
<h2>Manufacturer manuals (PDF)</h2>
<ul>
{pdfs}
</ul>
"""
    (DOCS / "index.html").write_text(
        page("Discovery tool knowledge",
             "Specification, operator guide, command reference and manuals for a "
             "read-only discovery tool for the B&K 2831E multimeter and DAQ3120.",
             index_body, today), encoding="utf-8")

    urls = [SITE] + [SITE + o for o, *_ in PAGES] + [SITE + o for o, *_ in PDFS]
    sitemap = "\n".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in urls)
    (DOCS / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap}\n</urlset>\n", encoding="utf-8")
    (DOCS / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")  # serve files exactly as-is

    for f in sorted(DOCS.iterdir()):
        print(f"{f.stat().st_size:>10,}  docs/{f.name}")


if __name__ == "__main__":
    build()
