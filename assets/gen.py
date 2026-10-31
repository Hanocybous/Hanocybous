"""Builds the animated SVG banners for the profile README. Run: python3 assets/gen.py assets"""
import base64, os, sys
from fontTools.ttLib import TTFont

OUT = sys.argv[1]
FONT = os.path.join(os.path.dirname(__file__), "archivo-800.woff")
f = TTFont(FONT)
UPM, CMAP, HMTX = f["head"].unitsPerEm, f.getBestCmap(), f["hmtx"]
B64 = base64.b64encode(open(FONT, "rb").read()).decode()

BLACK, BONE, BLUE, INK = "#050506", "#ebe6dc", "#1736ff", "#111114"
W = 1200


def adv(ch, size, track):
    return HMTX[CMAP.get(ord(ch), CMAP[32])][0] / UPM * size + track * size


def width(s, size, track=0):
    return sum(adv(c, size, track) for c in s)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, size, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if width(t, size) > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    return lines + [cur]


def svg(h, bg, body, css):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">
<style>
@font-face {{ font-family: A; src: url(data:font/woff;base64,{B64}) format("woff"); }}
text {{ font-family: A, Arial, sans-serif; font-weight: 800; }}
{css}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
<rect width="{W}" height="{h}" fill="{bg}"/>
{body}
</svg>
'''


def rising_chars(line, x, y, size, track, start, step, cls="ch"):
    """One <text> per letter so each can rise out of its own mask line."""
    out = []
    for i, ch in enumerate(line):
        if ch != " ":
            out.append(f'<text class="{cls}" x="{x:.1f}" y="{y}" font-size="{size}" '
                       f'style="animation-delay:{start + i * step:.3f}s">{esc(ch)}</text>')
        x += adv(ch, size, track)
    return "\n".join(out)


def hero():
    h, size, track, pad = 560, 128, -0.045, 48
    wires = [
        "M-20 150 C 260 80, 460 240, 700 170 S 1060 80, 1220 160",
        "M-20 300 C 220 370, 520 230, 760 320 S 1060 400, 1220 290",
        "M-20 420 C 300 350, 540 500, 820 430 S 1100 360, 1220 460",
    ]
    lines = "".join(f'<path class="wire" d="{d}"/>' for d in wires)
    lines += "".join(f'<path class="packet p{i}" d="{d}"/>' for i, d in enumerate(wires))
    y1, y2 = 300, 410
    body = f'''{lines}
<clipPath id="m1"><rect x="0" y="{y1 - size}" width="{W}" height="{size * 1.15:.0f}"/></clipPath>
<clipPath id="m2"><rect x="0" y="{y2 - size}" width="{W}" height="{size * 1.18:.0f}"/></clipPath>
<g clip-path="url(#m1)" fill="{BONE}">{rising_chars("Charilaos", pad, y1, size, track, 0.2, 0.04)}</g>
<g clip-path="url(#m2)" fill="{BONE}">{rising_chars("Chatzidimitriou", pad, y2, size, track, 0.35, 0.035)}</g>
<text class="fade" x="{pad}" y="490" font-size="26" fill="{BONE}">Systems &amp; network engineer in the making, based in Thessaloniki.</text>
<text class="fade f2" x="{pad}" y="528" font-size="21" fill="{BONE}" fill-opacity=".62">Open to Systems Engineer and SysAdmin roles</text>'''
    css = f'''.wire {{ fill: none; stroke: {BONE}; stroke-opacity: .09; stroke-width: 1.2; }}
.packet {{ fill: none; stroke: {BLUE}; stroke-width: 3; stroke-linecap: round; stroke-dasharray: 80 1500; animation: packet 5s linear infinite; }}
.p1 {{ stroke: {BONE}; animation-duration: 7s; animation-delay: -2s; }}
.p2 {{ animation-duration: 6s; animation-delay: -4s; }}
@keyframes packet {{ from {{ stroke-dashoffset: 1580; }} to {{ stroke-dashoffset: 0; }} }}
.ch {{ animation: rise 1.3s cubic-bezier(.16,1,.3,1) both; }}
@keyframes rise {{ from {{ transform: translateY(150px); }} }}
.fade {{ animation: fade 1.2s ease-out 1.1s both; }}
.f2 {{ animation-delay: 1.25s; }}
@keyframes fade {{ from {{ opacity: 0; transform: translateY(16px); }} }}'''
    assert width("Chatzidimitriou", size, track) < W - 2 * pad
    return svg(h, BLACK, body, css)


def statement():
    size, pad, lh = 50, 56, 58
    text = ("I like working close to the fundamentals: how packets move across a network, "
            "how data moves through memory, and how algorithms shape performance.")
    lines = wrap(text, size, W - 2 * pad)
    h = pad * 2 + lh * len(lines) - 6
    out, i = [], 0
    for n, line in enumerate(lines):
        x, y = pad, pad + size * 0.8 + n * lh
        for word in line.split():
            out.append(f'<text class="w" x="{x:.1f}" y="{y:.0f}" font-size="{size}" '
                       f'style="animation-delay:{i * 0.22:.2f}s">{esc(word)}</text>')
            x += width(word + " ", size, -0.03)
            i += 1
    css = f'''text {{ letter-spacing: -1.5px; fill: {INK}; }}
.w {{ animation: light 9s linear infinite both; }}
@keyframes light {{ 0% {{ opacity: .14; }} 4% {{ opacity: 1; }} 70% {{ opacity: 1; }} 76% {{ opacity: .14; }} 100% {{ opacity: .14; }} }}'''
    return svg(h, BONE, "\n".join(out), css)


def skills():
    rows = [
        ("Monitoring", "Seeing problems before users do. Zabbix, Nagios, SNMP traps, triggers and alerts."),
        ("Networking", "Networks you can trace, end to end. VLANs, Cisco RV, HPE Aruba CX, Wireshark, TCP/IP."),
        ("Systems", "Installing, maintaining and supporting real machines. Linux, systemd, iptables, shell."),
        ("Programming", "Algorithms you can explain, code you can trust. C, C++, Python, Java, MPI, CUDA."),
    ]
    pad, size, row_h, top = 56, 104, 128, 150
    desc_x, desc_size = 780, 20
    out = [f'<text x="{pad}" y="100" font-size="44" fill="{BONE}" style="letter-spacing:-1.5px">What I work with</text>']
    for k, (name, desc) in enumerate(rows):
        y0 = top + k * row_h
        out.append(f'<rect x="{pad}" y="{y0}" width="{W - 2 * pad}" height="2" fill="{BONE}" fill-opacity=".25"/>')
        out.append(f'<text class="name" x="{pad}" y="{y0 + 106}" font-size="{size}" fill="{BONE}" '
                   f'style="animation-delay:{0.2 + k * 0.15:.2f}s;transform-origin:{pad}px {y0 + 106}px">{esc(name)}</text>')
        for j, line in enumerate(wrap(desc, desc_size, W - pad - desc_x)):
            out.append(f'<text class="desc" x="{desc_x}" y="{y0 + 50 + j * 26}" font-size="{desc_size}" fill="{BONE}" '
                       f'style="animation-delay:{0.6 + k * 0.15:.2f}s">{esc(line)}</text>')
        assert width(name, size, -0.05) < desc_x - pad - 20, name
    css = '''.name { letter-spacing: -5px; animation: stretch 1.6s cubic-bezier(.16,1,.3,1) both; }
@keyframes stretch { from { transform: scaleX(.6) translateX(40px); opacity: 0; } 30% { opacity: 1; } }
.desc { font-weight: 800; animation: fade 1s ease-out both; }
@keyframes fade { from { opacity: 0; transform: translateY(12px); } }'''
    return svg(top + 4 * row_h + 40, BLUE, "\n".join(out), css)


def contact():
    pad, size, h = 56, 104, 400
    l1, l2 = "Let’s build something", "reliable."
    assert width(l1, size, -0.05) < W - 2 * pad
    body = f'''<clipPath id="c1"><rect x="0" y="{150 - size}" width="{W}" height="{size * 1.2:.0f}"/></clipPath>
<clipPath id="c2"><rect x="0" y="{248 - size}" width="{W}" height="{size * 1.2:.0f}"/></clipPath>
<g clip-path="url(#c1)"><text class="line" x="{pad}" y="150" font-size="{size}" fill="{BONE}">{l1}</text></g>
<g clip-path="url(#c2)"><text class="line l2" x="{pad}" y="248" font-size="{size}" fill="{BONE}">{l2}</text></g>
<text class="fade" x="{pad}" y="330" font-size="30" fill="{BONE}">charilaoschatzidimitriou@gmail.com</text>
<text class="fade" x="{pad}" y="368" font-size="21" fill="{BONE}" fill-opacity=".75">Hiring for a systems or network role, or just want to say hi? My inbox is always open.</text>'''
    css = '''.line { letter-spacing: -5px; animation: rise 1.3s cubic-bezier(.16,1,.3,1) .2s both; }
.l2 { animation-delay: .32s; }
@keyframes rise { from { transform: translateY(130px); } }
.fade { animation: fade 1s ease-out .9s both; }
@keyframes fade { from { opacity: 0; transform: translateY(12px); } }'''
    return svg(h, BLUE, body, css)


for name, fn in [("hero", hero), ("statement", statement), ("skills", skills), ("contact", contact)]:
    open(f"{OUT}/{name}.svg", "w").write(fn())
    print(name, "ok")
