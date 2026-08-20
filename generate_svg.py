#!/usr/bin/env python3
"""Generate today.svg profile card: ASCII art (left) + info panel (right)."""
import json, html

ART = json.load(open('art_data.json'))
STATS = json.load(open('stats.json'))

# ---------- layout constants ----------
BG      = '#0d1117'
ORANGE  = '#ffa657'
YELLOW  = '#ffde87'
WHITE   = '#e6edf3'
GRAY    = '#788088'
LINE    = '#969ea6'
CYAN    = '#79c0ff'

AFS   = 7.2                  # art font size
ACW   = AFS * 0.602          # monospace advance
ARH   = AFS * 1.075          # art row height
ART_W = ART['ncols'] * ACW
ART_H = ART['nrows'] * ARH

PFS   = 13.5                 # panel font size
PCW   = PFS * 0.602
W     = 52                   # panel width in char cells
PAN_W = W * PCW

M     = 18                   # outer margin
GAP   = 26                   # gap between art and panel
TOT_W = M + ART_W + GAP + PAN_W + M
TOT_H = M + ART_H + M

MONO = "'SFMono-Regular','Menlo','Consolas','Liberation Mono',monospace"

def esc(s): return html.escape(s, quote=False)

def cjk(c): return '\u4e00' <= c <= '\u9fff' or c in '\uff0c\u3002'
def dwid(s): return sum(2 if cjk(c) else 1 for c in s)

# ---------- panel lines ----------
panel = []  # each: ('kv', key, value) | ('sep', label, color) | ('blank',)
panel.append(('sep', 'YI.0@juliannafoster763-ops', CYAN))
panel.append(('kv', 'OS', 'macOS, iPadOS'))
panel.append(('kv', 'Host', 'MacBook Air (M5)'))
panel.append(('kv', 'IDE', 'VS Code, Claude Code'))
panel.append(('kv', 'Languages.Human', '\u4e2d\u6587, English'))
panel.append(('kv', 'Languages.Code', 'Python, HTML/CSS'))
panel.append(('kv', 'Interests', 'Art / Philosophy / Psych / HCI'))
panel.append(('blank',))
panel.append(('sep', '- GitHub Stats', WHITE))
panel.append(('kv', 'Repos', '{repos} {{Contributed: {contributed}}}'.format(**STATS)))
panel.append(('kv', 'Commits', '{commits:,}'.format(commits=STATS['commits'])))
panel.append(('kv', 'Stars', str(STATS['stars'])))
panel.append(('kv', 'Followers', str(STATS['followers'])))
panel.append(('kv', 'Lines of Code',
              '{loc:,} ( {add:,}++, {dele:,}-- )'.format(
                  loc=STATS['loc_add'] - STATS['loc_del'],
                  add=STATS['loc_add'], dele=STATS['loc_del'])))

# ---------- build svg ----------
out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{TOT_W:.0f}" '
           f'height="{TOT_H:.0f}" viewBox="0 0 {TOT_W:.0f} {TOT_H:.0f}">')
out.append(f'<rect width="100%" height="100%" fill="{BG}"/>')

# --- art ---
pal = ART['palette']
out.append(f'<g font-family="{MONO}" font-size="{AFS}" xml:space="preserve">')
for i, row in enumerate(ART['rows']):
    y = M + (i + 0.82) * ARH
    parts = []
    for idx, text in row:
        t = esc(text)
        if idx == -1:
            parts.append(f'<tspan>{t}</tspan>')
        else:
            parts.append(f'<tspan fill="{pal[idx]}">{t}</tspan>')
    out.append(f'<text x="{M}" y="{y:.1f}">' + ''.join(parts) + '</text>')
out.append('</g>')

# --- panel: rows spread to match art height exactly ---
PX = M + ART_W + GAP
PR = PX + PAN_W                       # right edge (values anchor here)
n = len(panel)
RH = ART_H / n
out.append(f'<g font-family="{MONO}" font-size="{PFS}" xml:space="preserve">')
for i, row in enumerate(panel):
    y = M + i * RH + RH / 2 + PFS * 0.35
    kind = row[0]
    if kind == 'blank':
        continue
    if kind == 'sep':
        label, color = row[1], row[2]
        ndash = W - dwid(label) - 1
        out.append(
            f'<text x="{PX}" y="{y:.1f}">'
            f'<tspan fill="{color}" font-weight="bold">{esc(label)}</tspan>'
            f'<tspan fill="{LINE}"> {"\u2500" * ndash}</tspan></text>')
    else:
        k, v = row[1], row[2]
        prefix = f'\u00b7 {k}: '
        ndots = W - len(prefix) - dwid(v) - 1
        out.append(
            f'<text x="{PX}" y="{y:.1f}">'
            f'<tspan fill="{GRAY}">\u00b7 </tspan>'
            f'<tspan fill="{ORANGE}">{esc(k)}:</tspan>'
            f'<tspan fill="{GRAY}"> {"." * ndots}</tspan></text>')
        out.append(
            f'<text x="{PR:.1f}" y="{y:.1f}" text-anchor="end" '
            f'fill="{YELLOW}">{esc(v)}</text>')
out.append('</g>')
out.append('</svg>')

open('today.svg', 'w').write('\n'.join(out))
print('today.svg written,', len('\n'.join(out)) // 1024, 'KB')
