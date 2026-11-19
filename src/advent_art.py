"""Original illustration for the Advent calendar: a snowy stone church at night.

Drawn from simple shapes (no tracing, no copied artwork). Every numbered door or
window is a "slot"; the church SVG draws its stone surround and a stained-glass
pane, and the page lays an HTML door with two shutters over each active slot so
it can swing open. Slots that have no day in a given year stay as glass.

church_svg(title)   the whole picture
SLOTS               the slot boxes in the 640 x 880 drawing
assign(days, s)     which slot each day of this Advent goes behind
wreath_svg(week)    a small Advent wreath with `week` candles lit (0-4, 5 = Christmas Eve)
"""
import html
import random

W, H = 640, 880
GROUND = 860
STONE, STONE2, STONE3 = "#dcc9a3", "#c7b186", "#b49c70"
ROOF, ROOF2 = "#3e4d6c", "#2f3b56"
LEAD = "#2a2320"
SNOW = "#f6f8fc"
GOLD = "#e2b64a"


def _slot(sid, x, y, w, h, shape="arch", kind="win"):
    return dict(id=sid, x=x, y=y, w=w, h=h, shape=shape, kind=kind)


SLOTS = [
    # bell tower
    _slot("T1", 290, 142, 60, 92),
    _slot("T2", 288, 254, 64, 64, "round"),
    _slot("T3", 292, 340, 56, 84),
    # front of the church
    _slot("F1", 170, 490, 62, 100),
    _slot("R", 266, 486, 108, 108, "round"),
    _slot("F2", 408, 490, 62, 100),
    _slot("F3", 170, 614, 62, 82),
    _slot("F4", 292, 614, 56, 76),
    _slot("F5", 408, 614, 62, 82),
    _slot("F6", 172, 742, 58, 118, "arch", "door"),
    _slot("D", 262, 712, 116, 148, "arch", "door"),
    _slot("F7", 410, 742, 58, 118, "arch", "door"),
]
# the two side aisles: two columns of four windows each
for side, cols in (("L", (18, 84)), ("Rt", (498, 564))):
    for r, y in enumerate((574, 648, 722, 796)):
        for c, x in enumerate(cols):
            SLOTS.append(_slot(f"{side}{r}{c}", x, y, 58, 60, "arch", "door" if r == 3 else "win"))

BY_ID = {s["id"]: s for s in SLOTS}
# Slots that turn back into plain glass first when Advent is shorter than 28 days
SPARE = ["T2", "F4", "L00", "Rt01", "L31", "Rt30"]


def assign(days, first_sunday, gaudete, christmas_eve):
    """Map each date in `days` (a list) to a slot id. The first day goes in the belfry,
    Gaudete Sunday behind the rose window, Christmas Eve behind the great door."""
    n = len(days)
    spare = SPARE[: len(SLOTS) - n]
    fixed = {first_sunday: "T1", gaudete: "R", christmas_eve: "D"}
    free = [s["id"] for s in SLOTS if s["id"] not in spare and s["id"] not in fixed.values()]
    random.Random(2026).shuffle(free)
    out, it = {}, iter(free)
    for d in days:
        out[d] = fixed.get(d) or next(it)
    return out, spare


def _f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def arch_path(x, y, w, h, pad=0):
    """A round-topped arch (semicircle on a rectangle), grown by `pad` on every side."""
    x, y, w, h = x - pad, y - pad, w + 2 * pad, h + pad
    r = w / 2
    ry = min(r * 0.92, h * 0.45)
    return (f"M{_f(x)} {_f(y + h)} L{_f(x)} {_f(y + ry)} A{_f(r)} {_f(ry)} 0 0 1 {_f(x + w)} {_f(y + ry)} "
            f"L{_f(x + w)} {_f(y + h)} Z")


def arch_ry(s):
    """Vertical radius of a slot's arch, as a % of its height (for the HTML shutters)."""
    r = s["w"] / 2
    return min(r * 0.92, s["h"] * 0.45) / s["h"] * 100


def _shape(s, pad, fill, extra=""):
    if s["shape"] == "round":
        cx, cy, r = s["x"] + s["w"] / 2, s["y"] + s["h"] / 2, s["w"] / 2 + pad
        return f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="{fill}"{extra}/>'
    return f'<path d="{arch_path(s["x"], s["y"], s["w"], s["h"], pad)}" fill="{fill}"{extra}/>'


def _glass(s):
    """A plain stained-glass pane for a slot (shows when the slot has no day)."""
    x, y, w, h = s["x"], s["y"], s["w"], s["h"]
    out = _shape(s, 0, "url(#glass)")
    if s["id"] == "T2":  # the tower clock
        cx, cy, r = x + w / 2, y + h / 2, w / 2
        out = f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="#f4ead2" stroke="{LEAD}" stroke-width="2"/>'
        for i in range(12):
            import math
            a = math.pi * 2 * i / 12
            out += (f'<line x1="{_f(cx + math.sin(a) * r * .78)}" y1="{_f(cy - math.cos(a) * r * .78)}" '
                    f'x2="{_f(cx + math.sin(a) * r * .9)}" y2="{_f(cy - math.cos(a) * r * .9)}" stroke="{LEAD}" stroke-width="2"/>')
        out += (f'<line x1="{_f(cx)}" y1="{_f(cy)}" x2="{_f(cx)}" y2="{_f(cy - r * .62)}" stroke="{LEAD}" stroke-width="3" stroke-linecap="round"/>'
                f'<line x1="{_f(cx)}" y1="{_f(cy)}" x2="{_f(cx + r * .42)}" y2="{_f(cy + r * .1)}" stroke="{LEAD}" stroke-width="3" stroke-linecap="round"/>')
        return out
    if s["shape"] == "round":
        cx, cy, r = x + w / 2, y + h / 2, w / 2
        import math
        for i in range(8):
            a = math.pi * 2 * i / 8
            out += f'<line x1="{_f(cx)}" y1="{_f(cy)}" x2="{_f(cx + math.cos(a) * r)}" y2="{_f(cy + math.sin(a) * r)}" stroke="{LEAD}" stroke-width="2"/>'
        out += f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * .32)}" fill="#c9798e" stroke="{LEAD}" stroke-width="2"/>'
        return out
    if s["kind"] == "door":
        return (_shape(s, 0, "#5a3a22") + f'<line x1="{_f(x + w / 2)}" y1="{_f(y + 4)}" x2="{_f(x + w / 2)}" y2="{_f(y + h)}" stroke="{LEAD}" stroke-width="2"/>')
    return (out + f'<line x1="{_f(x + w / 2)}" y1="{_f(y)}" x2="{_f(x + w / 2)}" y2="{_f(y + h)}" stroke="{LEAD}" stroke-width="2"/>'
            f'<line x1="{_f(x)}" y1="{_f(y + h * .55)}" x2="{_f(x + w)}" y2="{_f(y + h * .55)}" stroke="{LEAD}" stroke-width="2"/>')


def _surround(s):
    """Stone frame, sill and a little snow for each opening."""
    x, y, w, h = s["x"], s["y"], s["w"], s["h"]
    out = _shape(s, 6, STONE3, f' stroke="{LEAD}" stroke-width="1.5"')
    if s["shape"] != "round" and s["kind"] != "door":
        out += f'<rect x="{_f(x - 9)}" y="{_f(y + h)}" width="{_f(w + 18)}" height="7" rx="2" fill="{STONE2}" stroke="{LEAD}" stroke-width="1.5"/>'
        out += f'<path d="M{_f(x - 10)} {_f(y + h + 1)} q{_f((w + 20) / 4)} -6 {_f((w + 20) / 2)} -3 t{_f((w + 20) / 2)} 1 v2 h{_f(-(w + 20))}Z" fill="{SNOW}"/>'
    if s["kind"] == "door":
        out += f'<rect x="{_f(x - 12)}" y="{_f(y + h - 2)}" width="{_f(w + 24)}" height="6" fill="{STONE2}" stroke="{LEAD}" stroke-width="1.5"/>'
    return out


def _blocks(x0, y0, x1, y1, bh=22, bw=46, seed=1):
    """Faint stone-block courses on a wall."""
    rnd = random.Random(seed)
    lines = []
    y, row = y0 + bh, 0
    while y < y1:
        lines.append(f"M{_f(x0)} {_f(y)}H{_f(x1)}")
        y += bh
    y, row = y0, 0
    while y < y1:
        x = x0 + (bw / 2 if row % 2 else 0) + rnd.uniform(-4, 4)
        while x < x1:
            if x > x0 + 2:
                lines.append(f"M{_f(x)} {_f(y)}V{_f(min(y + bh, y1))}")
            x += bw + rnd.uniform(-6, 6)
        y += bh
        row += 1
    return f'<path d="{"".join(lines)}" stroke="{STONE3}" stroke-width="1.2" opacity=".55"/>'


def church_svg(title, used=None):
    """The whole picture. `used` is the set of slot ids that get an HTML door on top."""
    used = set(used or [])
    e = html.escape
    rnd = random.Random(29)
    stars = "".join(
        f'<circle cx="{_f(rnd.uniform(5, W - 5))}" cy="{_f(rnd.uniform(5, 520))}" r="{_f(rnd.choice((0.8, 1, 1.2, 1.6)))}" fill="#fff" opacity="{_f(rnd.uniform(.45, .95))}"/>'
        for _ in range(70))
    defs = f'''<defs>
<linearGradient id="ac-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#101a36"/><stop offset=".65" stop-color="#2a3a6b"/><stop offset="1" stop-color="#5a5f8f"/></linearGradient>
<radialGradient id="ac-moon" cx=".5" cy=".5" r=".5"><stop offset=".6" stop-color="#fff6d8"/><stop offset="1" stop-color="#fff6d8" stop-opacity="0"/></radialGradient>
<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3b5ea8"/><stop offset=".5" stop-color="#6a3f8a"/><stop offset="1" stop-color="#b8892e"/></linearGradient>
<linearGradient id="ac-stone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6d6b4"/><stop offset="1" stop-color="{STONE}"/></linearGradient>
<linearGradient id="ac-roof" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ROOF}"/><stop offset="1" stop-color="{ROOF2}"/></linearGradient>
</defs>'''
    sky = (f'<rect width="{W}" height="{H}" fill="url(#ac-sky)"/>{stars}'
           f'<circle cx="548" cy="78" r="44" fill="url(#ac-moon)" opacity=".55"/><circle cx="548" cy="78" r="26" fill="#fff6d8"/>'
           # the star over Bethlehem, faint, high on the left
           f'<path d="M96 70 l4 14 14 4 -14 4 -4 14 -4 -14 -14 -4 14 -4z" fill="#fff4c8"/>'
           # distant snowy hills
           f'<path d="M0 640 Q120 590 240 625 T480 610 T640 600 V{H} H0Z" fill="#46507e"/>'
           f'<path d="M0 700 Q160 660 320 690 T640 670 V{H} H0Z" fill="#5d6797"/>')
    # side aisles: walls and lean-to roofs
    aisles = ""
    for x0, x1, outer in ((6, 152, 0), (488, 634, 640)):
        aisles += f'<rect x="{x0}" y="560" width="{x1 - x0}" height="{GROUND - 560}" fill="url(#ac-stone)" stroke="{LEAD}" stroke-width="2"/>'
        aisles += _blocks(x0, 560, x1, GROUND, seed=x0)
        inner = x1 if outer == 0 else x0
        aisles += f'<polygon points="{inner},486 {outer},556 {outer},572 {inner},502" fill="url(#ac-roof)" stroke="{LEAD}" stroke-width="2"/>'
        aisles += f'<polygon points="{inner},484 {outer},554 {outer},562 {inner},492" fill="{SNOW}"/>'
    # the gable front of the nave, and its roof edge
    front = (f'<polygon points="146,478 320,370 494,478" fill="url(#ac-roof)" stroke="{LEAD}" stroke-width="2"/>'
             f'<polygon points="140,480 320,366 500,480 494,486 320,378 146,486" fill="{SNOW}" stroke="{LEAD}" stroke-width="1"/>'
             f'<rect x="152" y="476" width="336" height="{GROUND - 476}" fill="url(#ac-stone)" stroke="{LEAD}" stroke-width="2"/>'
             + _blocks(152, 476, 488, GROUND, seed=3) +
             # buttresses
             "".join(f'<rect x="{bx}" y="560" width="14" height="{GROUND - 560}" fill="{STONE2}" stroke="{LEAD}" stroke-width="1.5"/>'
                     f'<path d="M{bx - 2} 562 l9 -14 9 14z" fill="{SNOW}" stroke="{LEAD}" stroke-width="1"/>' for bx in (146, 480, 248, 378)))
    # bell tower, spire and cross
    tower = (f'<rect x="262" y="124" width="116" height="356" fill="url(#ac-stone)" stroke="{LEAD}" stroke-width="2"/>'
             + _blocks(262, 124, 378, 480, bh=20, bw=38, seed=9) +
             f'<rect x="254" y="118" width="132" height="12" fill="{STONE2}" stroke="{LEAD}" stroke-width="2"/>'
             f'<rect x="256" y="326" width="128" height="8" fill="{STONE2}" stroke="{LEAD}" stroke-width="1.5"/>'
             f'<path d="M256 326 q32 -6 64 -3 t64 1 v2 h-128z" fill="{SNOW}"/>'
             f'<polygon points="258,118 320,30 382,118" fill="#4f7d6e" stroke="{LEAD}" stroke-width="2"/>'
             f'<polygon points="320,30 296,64 300,66 320,40" fill="{SNOW}" opacity=".9"/>'
             f'<path d="M254 118 q34 -8 66 -4 t66 0 v4 h-132z" fill="{SNOW}"/>'
             # small corner pinnacles
             f'<polygon points="252,118 260,92 268,118" fill="#4f7d6e" stroke="{LEAD}" stroke-width="1.5"/>'
             f'<polygon points="372,118 380,92 388,118" fill="#4f7d6e" stroke="{LEAD}" stroke-width="1.5"/>'
             f'<rect x="317" y="2" width="6" height="32" fill="{GOLD}" stroke="{LEAD}" stroke-width="1.2"/>'
             f'<rect x="308" y="10" width="24" height="6" fill="{GOLD}" stroke="{LEAD}" stroke-width="1.2"/>')
    # the slots: stone frames, then glass for slots without a door
    frames = "".join(_surround(s) for s in SLOTS)
    glass = "".join(_glass(s) for s in SLOTS if s["id"] not in used)
    # two lanterns by the great door, a snowy ground, little evergreen trees
    lamps = ""
    for lx in (244, 396):
        lamps += (f'<circle cx="{lx}" cy="736" r="20" fill="#ffd98a" opacity=".25"/>'
                  f'<rect x="{lx - 6}" y="728" width="12" height="16" rx="2" fill="#ffe3a0" stroke="{LEAD}" stroke-width="1.5"/>'
                  f'<path d="M{lx - 8} 728 h16 l-8 -8z" fill="{LEAD}"/>')
    trees = ""
    for tx, ts in ((8, 1.0), (618, 0.9), (154, 0.55), (486, 0.55)):
        trees += (f'<g transform="translate({tx} {GROUND}) scale({ts})">'
                  f'<rect x="-3" y="-10" width="6" height="12" fill="#5a3a22"/>'
                  f'<polygon points="0,-78 -22,-30 22,-30" fill="#2f6a4a" stroke="{LEAD}" stroke-width="1.5"/>'
                  f'<polygon points="0,-56 -28,-8 28,-8" fill="#2f6a4a" stroke="{LEAD}" stroke-width="1.5"/>'
                  f'<path d="M-10 -52 l10 -20 10 20 q-10 -6 -20 0z M-14 -30 l14 -22 14 22 q-14 -6 -28 0z" fill="{SNOW}"/></g>')
    ground = (f'<path d="M0 {GROUND - 4} Q160 {GROUND - 12} 320 {GROUND - 4} T640 {GROUND - 6} V{H} H0Z" fill="{SNOW}"/>'
              f'<path d="M262 {GROUND} L250 {H} H390 L378 {GROUND}Z" fill="#e3e8f2"/>')
    return (f'<svg class="ac-art" viewBox="0 0 {W} {H}" role="img" aria-label="{e(title)}" xmlns="http://www.w3.org/2000/svg">'
            f'{defs}{sky}{aisles}{front}{tower}{frames}{glass}{lamps}{ground}{trees}</svg>')


def wreath_svg(week, label):
    """A small Advent wreath. week 1-4 lights that many candles; 5 lights all four plus the white Christ candle."""
    cols = ["#6a3f8a", "#6a3f8a", "#c9798e", "#6a3f8a"]
    xs = [34, 62, 98, 126]
    out = [f'<svg class="ac-wreath" viewBox="0 0 160 92" role="img" aria-label="{html.escape(label)}" xmlns="http://www.w3.org/2000/svg">',
           '<ellipse cx="80" cy="74" rx="72" ry="14" fill="#2f6a4a"/>',
           '<ellipse cx="80" cy="72" rx="62" ry="9" fill="#3f8a5c"/>']
    order = [0, 1, 2, 3]  # week n lights candles 1..n (violet, violet, rose, violet)
    for i in order:
        x = xs[i]
        y0 = 34 if i in (1, 2) else 40
        out.append(f'<rect x="{x - 6}" y="{y0}" width="12" height="{70 - y0}" rx="2" fill="{cols[i]}" stroke="{LEAD}" stroke-width="1.2"/>')
        if i < min(week, 4):
            out.append(f'<path d="M{x} {y0 - 16} q7 9 0 14 q-7 -5 0 -14z" fill="#ffcf5a"/><circle cx="{x}" cy="{y0 - 6}" r="9" fill="#ffd98a" opacity=".35"/>')
        out.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y0 - 3}" stroke="{LEAD}" stroke-width="1.5"/>')
    if week >= 5:
        out.append(f'<rect x="74" y="26" width="12" height="44" rx="2" fill="#fbf7ee" stroke="{LEAD}" stroke-width="1.2"/>'
                   '<path d="M80 8 q7 9 0 14 q-7 -5 0 -14z" fill="#ffcf5a"/><circle cx="80" cy="18" r="9" fill="#ffd98a" opacity=".35"/>')
    for bx, by in ((20, 76), (48, 82), (112, 82), (140, 76), (80, 84)):
        out.append(f'<circle cx="{bx}" cy="{by}" r="3.2" fill="#b3262e"/>')
    out.append("</svg>")
    return "".join(out)


if __name__ == "__main__":
    import sys
    sys.stdout.write(church_svg("test", used=[]))
