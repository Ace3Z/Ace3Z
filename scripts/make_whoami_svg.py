"""
A small animated "typing terminal" SVG for the top of the profile README, to
replace the static ```$ whoami``` code block. GitHub animates SVGs loaded as
<img>, so each line reveals left-to-right (a typing effect) with a cursor riding
the edge, then a blinking cursor holds at the end. Monochrome GitHub-dark theme,
matching the other profile art.

    python scripts/make_whoami_svg.py            # -> whoami.svg
    STATIC=1 python scripts/make_whoami_svg.py   # frozen final frame (previews)

Edit LINES below to change the text.
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "whoami.svg")
STATIC = bool(os.environ.get("STATIC"))

# ---- EDIT: (prompt_fragments, plain_text_for_width) -----------------------
# Each line: list of (text, color) spans + the concatenated plain string.
GREEN, INK, MUTED, ACCENT = "#3fb950", "#c9d1d9", "#7d8590", "#58a6ff"
LINES = [
    [("mahbod@github", GREEN), (":~$ ", MUTED), ("whoami", INK)],
]

CHARW = 9.6           # monospace advance at FONT
FONT = 16
LINE_H = 27
PAD = 18
TITLEBAR_H = 30
BG, BG2, FRAME = "#0d1117", "#111722", "#30363d"
CURSOR = "#c9d1d9"
TYPE_SPEED = 0.055    # seconds per character


def plain(line):
    return "".join(t for t, _ in line)


def spans_svg(line):
    return "".join(f'<tspan fill="{c}">{html.escape(t)}</tspan>' for t, c in line)


line_lens = [len(plain(l)) for l in LINES]
content_w = max(line_lens) * CHARW
CANVAS_W = int(PAD + content_w + PAD + 24)
CANVAS_H = int(TITLEBAR_H + PAD * 0.6 + len(LINES) * LINE_H + PAD * 0.6)

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, '
    f'Menlo, Consolas, monospace">',
    f'<defs><linearGradient id="wbg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="10" fill="url(#wbg)"/>',
    f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="10" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{c}"/>')

y0 = TITLEBAR_H + PAD * 0.6
begin = 0.4                      # small delay before typing starts
for i, line in enumerate(LINES):
    n = line_lens[i]
    dur = n * TYPE_SPEED
    y = y0 + i * LINE_H + FONT * 0.78
    lx = PAD
    w = n * CHARW
    text = (f'<text xml:space="preserve" x="{lx}" y="{y:.1f}" font-size="{FONT}" '
            f'textLength="{w:.1f}" lengthAdjust="spacing">{spans_svg(line)}</text>')

    if STATIC:
        parts.append(text)
        continue

    row_y = y0 + i * LINE_H
    parts.append(
        f'<clipPath id="w{i}"><rect x="{lx}" y="{row_y:.1f}" height="{LINE_H}" width="0">'
        f'<animate attributeName="width" from="0" to="{w:.1f}" begin="{begin:.2f}s" '
        f'dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>'
    )
    parts.append(f'<g clip-path="url(#w{i})">{text}</g>')
    # cursor rides the typing edge, then vanishes when the next line starts
    end = begin + dur
    parts.append(
        f'<rect y="{row_y+4:.1f}" width="9" height="{FONT+2}" fill="{CURSOR}" opacity="0">'
        f'<animate attributeName="x" from="{lx}" to="{lx+w:.1f}" begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0.9" begin="{begin:.2f}s"/>'
        + (f'<set attributeName="opacity" to="0" begin="{end:.2f}s"/>' if i < len(LINES)-1 else
           f'<animate attributeName="opacity" values="0.9;0.9;0;0" keyTimes="0;0.5;0.51;1" '
           f'dur="1s" begin="{end:.2f}s" repeatCount="indefinite"/>')
        + '</rect>'
    )
    begin = end + 0.35           # next line begins after this one finishes

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", CANVAS_W, "x", CANVAS_H)
