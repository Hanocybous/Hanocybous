"""Builds the animated network map for the profile README. Run: python3 assets/gen.py assets"""
import base64, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE
font = lambda w: base64.b64encode(open(os.path.join(HERE, f"jbmono-{w}.woff"), "rb").read()).decode()
REG, BOLD = font(400), font(700)

# Edit the map here. Each group is a distribution switch with its leaves.
CORE = ("Charilaos Chatzidimitriou", "Systems & network engineer, Thessaloniki")
GROUPS = [
    ("Experience", "exp", [
        ("Masoutis S.A.", "sysadmin intern, 2025"),
        ("Zabbix rollout", "22,000+ sensors"),
        ("UoI CSE Dept.", "IT support, 2022-25"),
    ]),
    ("Projects", "proj", [
        ("Pylos", "SSH autoblocker"),
        ("K-Clique App", "SAT solver, 16,000x"),
        ("Parallel Systems", "OpenMP, MPI, CUDA"),
        ("G++ Compiler", "lexer and parser"),
    ]),
    ("Skills", "skill", [
        ("Monitoring", "Zabbix, Nagios, SNMP"),
        ("Networking", "VLANs, Cisco, Aruba"),
        ("Systems", "Linux, iptables"),
        ("Code", "C, C++, Python, Java"),
    ]),
    ("Education", "edu", [
        ("MEng Comp. Eng.", "Univ. of Ioannina"),
        ("Certifications", "Ubuntu, Fortinet"),
        ("Languages", "GR, EN, FR"),
    ]),
]

THEMES = {
    "dark": dict(text="#e6edf3", muted="#8b949e", link="#30363d", fill="#161b22", core="#0d1117",
                 exp="#d29922", proj="#3fb950", skill="#58a6ff", edu="#db61a2", led="#3fb950"),
    "light": dict(text="#1f2328", muted="#59636e", link="#d1d9e0", fill="#f6f8fa", core="#ffffff",
                  exp="#9a6700", proj="#1a7f37", skill="#0969da", edu="#bf3989", led="#1a7f37"),
}

W = 1000
COL = W / len(GROUPS)
CORE_Y, CORE_H, CORE_W = 30, 84, 520
DIST_Y, DIST_H, DIST_W = 196, 46, 200
LEAF_Y0, LEAF_H, LEAF_W, LEAF_GAP = 300, 58, 208, 16
H = LEAF_Y0 + 4 * (LEAF_H + LEAF_GAP) + 10


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fits(s, size, box):
    assert len(s) * size * 0.6 < box - 24, f"too long for its box: {s!r}"


def build(t):
    links, packets, nodes = [], [], []
    cx, core_bottom = W / 2, CORE_Y + CORE_H
    n = 0
    for g, (gname, key, leaves) in enumerate(GROUPS):
        color = t[key]
        dx = COL * g + COL / 2
        bus_x = dx - DIST_W / 2 + 4
        # core to distribution
        up = f"M{cx} {core_bottom} C {cx} {core_bottom + 50}, {dx} {DIST_Y - 50}, {dx} {DIST_Y}"
        links.append(f'<path class="link" pathLength="1" style="animation-delay:{0.3 + g * 0.1:.2f}s" d="{up}"/>')
        links.append(f'<text class="port" x="{dx + 8}" y="{DIST_Y - 10}" style="animation-delay:{0.9 + g * 0.1:.2f}s">ge-0/0/{g}</text>')
        nodes.append(f'<g class="node" style="animation-delay:{0.6 + g * 0.1:.2f}s">'
                     f'<rect x="{dx - DIST_W / 2}" y="{DIST_Y}" width="{DIST_W}" height="{DIST_H}" rx="8" fill="{color}"/>'
                     f'<text class="dist" x="{dx}" y="{DIST_Y + 30}" text-anchor="middle">{esc(gname)}</text></g>')
        fits(gname, 18, DIST_W)
        last_y = LEAF_Y0 + (len(leaves) - 1) * (LEAF_H + LEAF_GAP) + LEAF_H / 2
        links.append(f'<path class="link" pathLength="1" style="animation-delay:{0.9 + g * 0.1:.2f}s" '
                     f'd="M{bus_x} {DIST_Y + DIST_H} V {last_y}"/>')
        for i, (title, sub) in enumerate(leaves):
            y = LEAF_Y0 + i * (LEAF_H + LEAF_GAP)
            mid, lx = y + LEAF_H / 2, bus_x + 14
            delay = 1.2 + g * 0.08 + i * 0.12
            links.append(f'<path class="link" pathLength="1" style="animation-delay:{delay:.2f}s" d="M{bus_x} {mid} H {lx}"/>')
            nodes.append(f'<g class="node" style="animation-delay:{delay + 0.1:.2f}s">'
                         f'<rect x="{lx}" y="{y}" width="{LEAF_W - 30}" height="{LEAF_H}" rx="6" fill="{t["fill"]}" stroke="{color}" stroke-width="1.5"/>'
                         f'<text class="leaf" x="{lx + 12}" y="{y + 25}">{esc(title)}</text>'
                         f'<text class="sub" x="{lx + 12}" y="{y + 45}">{esc(sub)}</text>'
                         f'<circle class="led" cx="{lx + LEAF_W - 44}" cy="{y + 14}" r="3.5" fill="{t["led"]}" '
                         f'style="animation-duration:{0.9 + (n * 0.37) % 1.4:.2f}s"/></g>')
            fits(title, 15, LEAF_W - 30)
            fits(sub, 12, LEAF_W - 30)
            # a packet runs core -> switch -> leaf, every other one runs back up
            route = f"{up} L {dx} {DIST_Y + DIST_H} L {bus_x} {DIST_Y + DIST_H} L {bus_x} {mid} L {lx} {mid}"
            back = ' keyPoints="1;0" keyTimes="0;1" calcMode="linear"' if n % 2 else ""
            start = 2.2 + n * 0.35  # hidden until its first trip, or it sits at the origin
            packets.append(f'<circle r="4" fill="{color}" opacity="0"><set attributeName="opacity" to="1" begin="{start:.2f}s"/>'
                           f'<animateMotion dur="{2.6 + (n % 3) * 0.5:.1f}s" begin="{start:.2f}s" repeatCount="indefinite" path="{route}"{back}/></circle>')
            n += 1

    core = (f'<g class="node" style="animation-delay:0s">'
            f'<rect x="{cx - CORE_W / 2}" y="{CORE_Y}" width="{CORE_W}" height="{CORE_H}" rx="12" '
            f'fill="{t["core"]}" stroke="{t["text"]}" stroke-width="2"/>'
            f'<text class="core" x="{cx}" y="{CORE_Y + 38}" text-anchor="middle">{esc(CORE[0])}</text>'
            f'<text class="coresub" x="{cx}" y="{CORE_Y + 64}" text-anchor="middle">{esc(CORE[1])}</text>'
            f'<circle class="led" cx="{cx + CORE_W / 2 - 18}" cy="{CORE_Y + 18}" r="4.5" fill="{t["led"]}" style="animation-duration:1.1s"/></g>')
    fits(CORE[0], 26, CORE_W)
    fits(CORE[1], 15, CORE_W)

    css = f'''@font-face {{ font-family: M; src: url(data:font/woff;base64,{REG}) format("woff"); font-weight: 400; }}
@font-face {{ font-family: M; src: url(data:font/woff;base64,{BOLD}) format("woff"); font-weight: 700; }}
text {{ font-family: M, ui-monospace, monospace; fill: {t["text"]}; }}
.core {{ font-size: 26px; font-weight: 700; }}
.coresub {{ font-size: 15px; fill: {t["muted"]}; }}
.dist {{ font-size: 18px; font-weight: 700; fill: {t["core"]}; }}
.leaf {{ font-size: 15px; font-weight: 700; }}
.sub {{ font-size: 12px; fill: {t["muted"]}; }}
.port {{ font-size: 11px; fill: {t["muted"]}; animation: fade .6s ease-out both; }}
.link {{ fill: none; stroke: {t["link"]}; stroke-width: 2; stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw .7s cubic-bezier(.65,0,.35,1) forwards; }}
.node {{ animation: pop .6s cubic-bezier(.16,1,.3,1) both; }}
.led {{ animation: blink 1s steps(1) infinite; }}
@keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
@keyframes pop {{ from {{ opacity: 0; transform: translateY(10px); }} }}
@keyframes fade {{ from {{ opacity: 0; }} }}
@keyframes blink {{ 50% {{ opacity: .25; }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} .link {{ stroke-dashoffset: 0; }} .packets {{ display: none; }} }}'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}">
<style>{css}</style>
<g>{"".join(links)}</g>
<g class="packets">{"".join(packets)}</g>
<g>{core}{"".join(nodes)}</g>
</svg>
'''


for name, t in THEMES.items():
    open(os.path.join(OUT, f"network-{name}.svg"), "w").write(build(t))
    print(name, "ok")
