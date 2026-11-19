"""Original illustrations for the fourteen Stations of the Cross.

Each scene is drawn from simple shapes in the style of a stained-glass window:
an arched frame, flat jewel-tone colors and dark "lead" outlines. Nothing here is
traced or copied from existing artwork. scene(n) returns the inner SVG markup for
station n (1-14); svg(n, title) wraps it in an <svg> element.
"""
import math

W, H = 240, 300
LEAD = "#2a2320"
SKIN = "#c8956b"
C = {  # palette
    "jesus": "#9b2a2a", "jesus2": "#7a1f22", "mary": "#2f5d9e", "mary2": "#20406f", "white": "#efe6d2",
    "soldier": "#6f6a5c", "soldier2": "#4f4b41", "metal": "#a9a79c", "pilate": "#e8dfc8", "purple": "#5b3a7a",
    "simon": "#7a6236", "veronica": "#3f7a6a", "woman1": "#8a5a8f", "woman2": "#b0773a", "john": "#3d7a46",
    "joseph": "#6b4e8a", "wood": "#6b4424", "wood2": "#4e3018", "gold": "#e2b64a", "stone": "#9a8f7e",
    "stone2": "#7b715f", "ground": "#8b7a56", "ground2": "#6e6044", "city": "#c9b48a", "hair": "#3b2a1e",
}
SKY = {"day": ("#8fb3d9", "#d9c99a"), "dusk": ("#5a6f9e", "#d8a070"), "dark": ("#1e2236", "#4a3550"),
       "night": ("#1b2a4a", "#3c4f78")}


def _f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def _pts(pts):
    return " ".join(f"{_f(x)},{_f(y)}" for x, y in pts)


def poly(pts, fill, extra=""):
    return f'<polygon points="{_pts(pts)}" fill="{fill}"{extra}/>'


def path(d, fill="none", sw=None, stroke=LEAD, extra=""):
    s = f' stroke-width="{sw}"' if sw is not None else ""
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}"{s}{extra}/>'


def circle(x, y, r, fill, extra=""):
    return f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r)}" fill="{fill}"{extra}/>'


def _unit(ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1
    return dx / L, dy / L


def robe(s, f, ws, wf, fill, bulge=0.12):
    """A robe from shoulder point s to hem point f, ws/wf wide at top/bottom."""
    ux, uy = _unit(*s, *f)
    px, py = -uy, ux  # perpendicular
    a = (s[0] + px * ws / 2, s[1] + py * ws / 2)
    b = (s[0] - px * ws / 2, s[1] - py * ws / 2)
    c = (f[0] - px * wf / 2, f[1] - py * wf / 2)
    d = (f[0] + px * wf / 2, f[1] + py * wf / 2)
    L = math.hypot(f[0] - s[0], f[1] - s[1])
    k = L * bulge
    # gentle outward curve on both sides
    m1 = ((a[0] + d[0]) / 2 + px * k * 0.4, (a[1] + d[1]) / 2 + py * k * 0.4)
    m2 = ((b[0] + c[0]) / 2 - px * k * 0.4, (b[1] + c[1]) / 2 - py * k * 0.4)
    hem = ((c[0] + d[0]) / 2 + ux * 3, (c[1] + d[1]) / 2 + uy * 3)
    return (f'<path d="M{_f(a[0])} {_f(a[1])} Q{_f(m1[0])} {_f(m1[1])} {_f(d[0])} {_f(d[1])} '
            f'Q{_f(hem[0])} {_f(hem[1])} {_f(c[0])} {_f(c[1])} Q{_f(m2[0])} {_f(m2[1])} {_f(b[0])} {_f(b[1])} '
            f'Q{_f(s[0] - ux * 4)} {_f(s[1] - uy * 4)} {_f(a[0])} {_f(a[1])}Z" fill="{fill}"/>')


def arm(pts, fill, w=7, hand=True):
    d = "M" + " L".join(f"{_f(x)} {_f(y)}" for x, y in pts)
    out = (f'<path d="{d}" fill="none" stroke="{LEAD}" stroke-width="{w + 3}" stroke-linecap="round" stroke-linejoin="round"/>'
           f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
    if hand:
        x, y = pts[-1]
        out += circle(x, y, w * 0.48, SKIN)
    return out


def head(x, y, r=9, kind="plain", veil=None, halo=False, tilt=0):
    out = []
    if halo:
        out.append(circle(x, y, r * 1.75, C["gold"]))
        # cruciform nimbus
        for ang in (tilt - 90, tilt + 0, tilt + 180):
            a = math.radians(ang)
            out.append(f'<line x1="{_f(x + math.cos(a) * r * 1.05)}" y1="{_f(y + math.sin(a) * r * 1.05)}" '
                       f'x2="{_f(x + math.cos(a) * r * 1.72)}" y2="{_f(y + math.sin(a) * r * 1.72)}" stroke="#b5862a" stroke-width="3.2"/>')
    if kind == "veil":
        out.append(circle(x, y + 1, r * 1.32, veil))
        out.append(circle(x, y + 1.5, r * 0.82, SKIN))
    elif kind == "helmet":
        out.append(circle(x, y, r, SKIN))
        out.append(path(f"M{_f(x - r * 1.05)} {_f(y + 1)} A{_f(r * 1.05)} {_f(r * 1.05)} 0 0 1 {_f(x + r * 1.05)} {_f(y + 1)}Z", C["metal"]))
        out.append(path(f"M{_f(x - 2)} {_f(y - r)} Q{_f(x + 2)} {_f(y - r * 2.1)} {_f(x + r * 1.3)} {_f(y - r * 1.2)}", "none", 4, "#a33a2c"))
    elif kind in ("hair", "thorns"):
        # long hair falling behind the face, a short beard
        out.append(path(f"M{_f(x - r * 1.08)} {_f(y)} A{_f(r * 1.08)} {_f(r * 1.08)} 0 0 1 {_f(x + r * 1.08)} {_f(y)} "
                        f"L{_f(x + r * 1.0)} {_f(y + r * 1.45)} L{_f(x - r * 1.0)} {_f(y + r * 1.45)}Z", C["hair"]))
        out.append(circle(x, y + r * 0.08, r * 0.84, SKIN))
        out.append(path(f"M{_f(x - r * 0.62)} {_f(y + r * 0.42)} Q{_f(x)} {_f(y + r * 1.32)} {_f(x + r * 0.62)} {_f(y + r * 0.42)} "
                        f"Q{_f(x)} {_f(y + r * 0.78)} {_f(x - r * 0.62)} {_f(y + r * 0.42)}Z", C["hair"], 1.2))
        if kind == "thorns":
            out.append(f'<path d="M{_f(x - r * 1.02)} {_f(y - r * 0.2)} Q{_f(x)} {_f(y - r * 0.95)} {_f(x + r * 1.02)} {_f(y - r * 0.2)}" fill="none" '
                       f'stroke="#4d5a2a" stroke-width="3" stroke-dasharray="2.2 1.4"/>')
    else:
        out.append(circle(x, y, r, SKIN))
        if kind == "short":
            out.append(path(f"M{_f(x - r)} {_f(y + 1)} A{_f(r)} {_f(r)} 0 0 1 {_f(x + r)} {_f(y + 1)} Q{_f(x)} {_f(y - r * 0.4)} {_f(x - r)} {_f(y + 1)}Z", C["hair"]))
    return "".join(out)


def cross(foot, top, bar_t=0.78, half=30, w=9, fill=None):
    """A Latin cross from foot to top; the crossbar sits at bar_t along it."""
    fill = fill or C["wood"]
    ux, uy = _unit(*foot, *top)
    px, py = -uy, ux
    L = math.hypot(top[0] - foot[0], top[1] - foot[1])
    def beam(a, b, w):
        return poly([(a[0] + px * w / 2, a[1] + py * w / 2), (b[0] + px * w / 2, b[1] + py * w / 2),
                     (b[0] - px * w / 2, b[1] - py * w / 2), (a[0] - px * w / 2, a[1] - py * w / 2)], fill)
    def bar(cx, cy, h, w):
        a = (cx + px * h, cy + py * h)
        b = (cx - px * h, cy - py * h)
        return poly([(a[0] + ux * w / 2, a[1] + uy * w / 2), (b[0] + ux * w / 2, b[1] + uy * w / 2),
                     (b[0] - ux * w / 2, b[1] - uy * w / 2), (a[0] - ux * w / 2, a[1] - uy * w / 2)], fill)
    cx, cy = foot[0] + ux * L * bar_t, foot[1] + uy * L * bar_t
    return beam(foot, top, w) + bar(cx, cy, half, w)


def frame_open(sky, n=0):
    top, bot = SKY[sky]
    return (f'<defs><linearGradient id="sk{n}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
            f'<stop offset="1" stop-color="{bot}"/></linearGradient>'
            f'<clipPath id="arch{n}"><path d="M14 296V96A106 84 0 0 1 226 96V296Z"/></clipPath></defs>'
            f'<g clip-path="url(#arch{n})" stroke="{LEAD}" stroke-width="2" stroke-linejoin="round">'
            f'<rect width="{W}" height="{H}" fill="url(#sk{n})" stroke="none"/>')


def frame_close(n):
    # lead frame, glazing bars and the station number in the arch
    return ('</g><path d="M14 296V96A106 84 0 0 1 226 96V296Z" fill="none" stroke="#2a2320" stroke-width="7"/>'
            '<path d="M14 296V96A106 84 0 0 1 226 96V296Z" fill="none" stroke="#c9a64a" stroke-width="2.2"/>'
            '<circle cx="120" cy="34" r="17" fill="#f4ecd8" stroke="#2a2320" stroke-width="3"/>'
            + (f'<text x="120" y="40.5" text-anchor="middle" font-family="Georgia, serif" font-weight="700" font-size="{17 if n < 10 else 15}" fill="#2a2320" stroke="none">{ROMAN[n]}</text>'
               if 1 <= n <= 14 else '<path d="M120 24v21M112 31h16" stroke="#2a2320" stroke-width="3.4" stroke-linecap="round"/>'))


ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV"]


def ground(y=246, fill=None, hill=False):
    fill = fill or C["ground"]
    if hill:
        return path(f"M0 {y + 20} Q70 {y - 26} 130 {y - 8} T240 {y + 4} V300 H0Z", fill)
    return path(f"M0 {y} Q60 {y - 8} 120 {y - 2} T240 {y} V300 H0Z", fill)


def city(y=200):
    # walls and towers of Jerusalem in the distance
    return (path(f"M14 {y + 30} V{y + 6} h14 v-10 h10 v10 h22 v-18 l9 -9 l9 9 v18 h26 v-8 h12 v8 h30 v-22 h16 v22 h26 v-12 h12 v12 h26 V{y + 30}Z", C["city"], 1.5)
            + path(f"M86 {y + 30} v-12 a6 6 0 0 1 12 0 v12", C["stone2"], 1.5))


def golgotha(y=150, x=196, s=0.5):
    # three small crosses on a distant hill
    out = path(f"M150 {y + 60} Q{x} {y - 6} 240 {y + 30} V{y + 70} H150Z", C["ground2"], 1.5)
    for dx, h in ((-18, 34), (0, 42), (18, 34)):
        out += cross((x + dx, y + 30), (x + dx, y + 30 - h * s * 2), 0.75, 7 * s * 2, 3)
    return out


def rays(x, y, n=9, r=60, col="#f5dc8a"):
    out = []
    for i in range(n):
        a = math.radians(200 + i * 140 / (n - 1))
        out.append(f'<line x1="{_f(x)}" y1="{_f(y)}" x2="{_f(x + math.cos(a) * r)}" y2="{_f(y + math.sin(a) * r)}" stroke="{col}" stroke-width="5" opacity=".45"/>')
    return "".join(out)


# --------------------------------------------------------------------------- figures
def jesus_carrying(x, y, lean=10, thorns=True, cross_back=True, bound=False):
    """Jesus walking left-to-right, bent forward, with the cross on his right shoulder.
    (x, y) is where his feet meet the ground."""
    out = []
    sh = (x - lean * 0.3 + lean, y - 92)
    hem = (x, y)
    hd = (sh[0] + lean * 0.55 + 4, sh[1] - 16)
    if cross_back:
        # cross: foot trails behind on the ground, top over the shoulder
        out.append(cross((x - 70, y + 2), (sh[0] + 30, sh[1] - 26), 0.72, 26, 10))
    out.append(robe(sh, hem, 26, 40, C["jesus"]))
    out.append(head(*hd, 9.5, "thorns" if thorns else "hair", halo=True))
    # arms reach up to hold the beam
    out.append(arm([(sh[0] + 6, sh[1] + 6), (sh[0] + 18, sh[1] + 14), (sh[0] + 22, sh[1] - 2)], C["jesus2"]))
    out.append(arm([(sh[0] - 4, sh[1] + 6), (sh[0] + 4, sh[1] + 24), (sh[0] + 14, sh[1] + 2)], C["jesus2"]))
    return "".join(out)


def jesus_fallen(x, y, depth=1):
    """Jesus fallen to his knees (depth 1), lower (2) or nearly flat (3), cross across his back."""
    out = []
    if depth == 1:
        sh, hem, hd = (x + 18, y - 50), (x - 16, y - 4), (x + 36, y - 46)
        out.append(robe(sh, hem, 24, 42, C["jesus"], 0.05))
        out.append(head(*hd, 9.5, "thorns", halo=True, tilt=30))
        out.append(arm([(sh[0] + 2, sh[1] + 4), (sh[0] + 14, sh[1] + 24), (sh[0] + 22, y - 2)], C["jesus2"]))
        out.append(cross((x - 78, y - 2), (x + 54, y - 82), 0.74, 24, 10))
        out.append(arm([(sh[0] - 4, sh[1] + 2), (sh[0] + 8, sh[1] - 16), (sh[0] + 20, sh[1] - 20)], C["jesus2"]))
    elif depth == 2:
        sh, hem, hd = (x + 24, y - 34), (x - 22, y - 4), (x + 40, y - 38)
        out.append(robe(sh, hem, 24, 40, C["jesus"], 0.04))
        out.append(head(*hd, 9.5, "thorns", halo=True, tilt=50))
        out.append(arm([(sh[0] + 4, sh[1] + 4), (sh[0] + 18, sh[1] + 20), (sh[0] + 30, y - 2)], C["jesus2"]))
        out.append(cross((x - 82, y - 8), (x + 58, y - 64), 0.74, 24, 10))
        out.append(arm([(sh[0] - 6, sh[1] + 6), (sh[0] + 2, y - 4)], C["jesus2"]))
    else:
        sh, hem, hd = (x + 26, y - 18), (x - 34, y - 6), (x + 42, y - 18)
        out.append(robe(sh, hem, 22, 30, C["jesus"], 0.03))
        out.append(head(*hd, 9.5, "thorns", halo=True, tilt=80))
        out.append(arm([(sh[0] + 2, sh[1] + 6), (sh[0] + 26, y - 2)], C["jesus2"]))
        out.append(cross((x - 84, y - 18), (x + 60, y - 50), 0.74, 24, 10))
        out.append(arm([(sh[0] - 8, sh[1] + 4), (sh[0] - 4, y - 1)], C["jesus2"]))
    return "".join(out)


def standing(x, y, h=100, fill="#777", fill2=None, kind="short", veil=None, arms=None, halo=False, lean=0, ws=24, wf=36, mantle=None):
    """A generic standing figure with feet at (x, y). arms: list of point lists relative to the shoulder."""
    fill2 = fill2 or fill
    sh = (x + lean, y - h * 0.86)
    out = [robe(sh, (x, y), ws, wf, fill)]
    if mantle:
        out.append(robe((sh[0], sh[1] - 2), (x + (lean * 0.2), y - h * 0.25), ws + 4, wf - 2, mantle, 0.1))
    hd = (sh[0] + lean * 0.12, sh[1] - h * 0.14)
    out.append(head(*hd, h * 0.095, kind, veil=veil, halo=halo))
    for a in arms or []:
        out.append(arm([(sh[0] + dx, sh[1] + dy) for dx, dy in a], fill2))
    return "".join(out)


def kneeling(x, y, fill, kind="veil", veil=None, arms=None, face=1, h=70):
    """A figure kneeling, facing right (face=1) or left (-1). (x, y) is the knee on the ground."""
    sh = (x + 6 * face, y - h * 0.82)
    out = [robe(sh, (x - 6 * face, y), 22, 40, fill, 0.08)]
    hd = (sh[0] + 3 * face, sh[1] - h * 0.18)
    out.append(head(*hd, h * 0.13, kind, veil=veil))
    for a in arms or []:
        out.append(arm([(sh[0] + dx * face, sh[1] + dy) for dx, dy in a], fill))
    return "".join(out)


def soldier(x, y, face=1, spear=True, arms=None, h=104):
    out = []
    if spear:
        sx = x - 20 * face
        out.append(path(f"M{_f(sx)} {_f(y + 2)} L{_f(sx + 4 * face)} {_f(y - h * 1.32)}", "none", 3.2, "#5a4630"))
        out.append(poly([(sx + 4 * face - 4, y - h * 1.32), (sx + 4 * face + 4, y - h * 1.32), (sx + 4.6 * face, y - h * 1.48)], C["metal"]))
    sh = (x, y - h * 0.86)
    out.append(robe(sh, (x, y - h * 0.34), 26, 30, C["soldier"], 0.04))  # tunic/armor
    out.append(robe((x, y - h * 0.36), (x, y - h * 0.26), 30, 32, C["soldier2"], 0.0))  # skirt
    # legs
    out.append(arm([(x - 6, y - h * 0.27), (x - 8, y - 2)], C["soldier2"], 6, False))
    out.append(arm([(x + 6, y - h * 0.27), (x + 8, y - 2)], C["soldier2"], 6, False))
    out.append(path(f"M{_f(x - 13)} {_f(y - h * 0.72)} h26", "none", 2.4, C["metal"]))
    out.append(head(x + 2 * face, sh[1] - h * 0.14, h * 0.095, "helmet"))
    for a in arms if arms is not None else ([[(-10 * face, 6), (-18 * face, 22)]] if spear else []):
        out.append(arm([(sh[0] + dx, sh[1] + dy) for dx, dy in a], C["soldier"]))
    return "".join(out)


def mary(x, y, h=96, arms=None, lean=0):
    return standing(x, y, h, C["mary2"], C["mary"], "veil", C["mary"], arms, halo=False, lean=lean, mantle=C["mary"])


# --------------------------------------------------------------------------- the fourteen scenes
def s1():
    out = [frame_open("day", 1)]
    # Pilate's hall: columns and a dais
    out.append(path("M14 250V120H226V250", "#d9cdb2"))
    for cx in (40, 200):
        out.append(path(f"M{cx - 10} 250V132h20V250Z", "#efe6d0"))
        out.append(path(f"M{cx - 14} 132h28v-8h-28Z", "#cfc2a2"))
    out.append(path("M14 250H226V300H14Z", "#b8a888"))
    out.append(path("M22 244h86v10h-86Z", "#a8987a"))
    # Pilate seated on his judgment seat, washing his hands over a basin
    out.append(path("M44 244V190h40v54Z", "#8a6a3a"))
    out.append(robe((70, 172), (64, 238), 24, 34, C["pilate"]))
    out.append(robe((72, 170), (78, 214), 26, 20, C["purple"], 0.06))
    out.append(head(72, 158, 9, "short"))
    out.append(path("M86 222h26l-4 12h-18Z", C["metal"]))
    out.append(path("M99 234v10M91 244h16", "none", 2))
    out.append(arm([(78, 178), (90, 196), (100, 212)], C["pilate"]))
    out.append(arm([(66, 180), (80, 200), (96, 212)], C["pilate"]))
    out.append(path("M98 214 q2 4 0 7M102 214 q2 4 0 7", "none", 1.4, "#5a8bc0"))
    # Jesus stands, hands bound, crowned with thorns, in a purple cloak
    out.append(robe((160, 170), (158, 252), 26, 40, C["jesus"]))
    out.append(robe((160, 168), (166, 226), 28, 30, C["purple"], 0.06))
    out.append(head(160, 152, 9.5, "thorns", halo=True))
    out.append(arm([(152, 178), (152, 200), (158, 208)], C["jesus2"]))
    out.append(arm([(168, 178), (166, 200), (160, 208)], C["jesus2"]))
    out.append(path("M152 206 q8 6 14 0", "none", 2.2, "#c9b48a"))
    out.append(soldier(204, 256, -1))
    out.append(frame_close(1))
    return "".join(out)


def s2():
    out = [frame_open("day", 2), city(180), ground(240)]
    out.append(soldier(204, 254, -1, arms=[[(-10, 8), (-26, 0), (-40, -8)]], spear=False))
    out.append(jesus_carrying(130, 258, 6))
    out.append(frame_close(2))
    return "".join(out)


def s3():
    out = [frame_open("day", 3), city(176), ground(244)]
    out.append(soldier(206, 256, -1))
    out.append(jesus_fallen(118, 258, 1))
    # stones on the road
    out.append(path("M150 262 q6 -6 12 0Z M60 270 q5 -5 10 0Z", C["stone"], 1.5))
    out.append(frame_close(3))
    return "".join(out)


def s4():
    out = [frame_open("day", 4), city(178), ground(244)]
    out.append(jesus_carrying(92, 260, 8))
    out.append(mary(190, 258, 98, arms=[[(-8, 8), (-22, 18), (-36, 14)], [(4, 10), (-10, 26), (-26, 24)]], lean=-6))
    out.append(head(186, 158, 0.01))  # keep stacking simple
    out.append(frame_close(4))
    return "".join(out)


def s5():
    out = [frame_open("day", 5), city(180), ground(242)]
    # Simon behind, lifting the trailing end of the cross
    out.append(cross((26, 214), (168, 128), 0.74, 26, 10))
    out.append(standing(58, 258, 94, C["simon"], "#5e4a26", "short", arms=[[(8, 6), (-6, 26), (-14, 38)], [(14, 8), (2, 30), (-10, 40)]], lean=6))
    out.append(robe((150, 166), (146, 258), 26, 40, C["jesus"]))
    out.append(head(158, 152, 9.5, "thorns", halo=True))
    out.append(arm([(154, 172), (164, 182), (166, 158)], C["jesus2"]))
    out.append(arm([(144, 174), (150, 196), (160, 170)], C["jesus2"]))
    out.append(frame_close(5))
    return "".join(out)


def s6():
    out = [frame_open("day", 6), city(178), ground(244)]
    out.append(jesus_carrying(100, 258, 10))
    # Veronica kneels and holds up her veil
    out.append(kneeling(184, 262, C["veronica"], "veil", "#2f5f52", face=-1, h=74))
    out.append(path("M140 196 h38 v40 h-38Z", C["white"], 2))
    out.append(circle(159, 214, 8, "#e6d7b4", ' stroke="#b49a6a" stroke-width="1.5"'))
    out.append(arm([(180, 208), (172, 206), (178, 198)], C["veronica"], 6))
    out.append(arm([(184, 210), (168, 222), (176, 232)], C["veronica"], 6, False))
    out.append(frame_close(6))
    return "".join(out)


def s7():
    out = [frame_open("dusk", 7)]
    # the city gate
    out.append(path("M14 250V140h70v110Z", C["city"]))
    out.append(path("M30 250v-64a19 19 0 0 1 38 0v64Z", "#5a4a34"))
    out.append(path("M14 140h70v-10h-70Z", "#b39d72"))
    out.append(ground(246))
    out.append(standing(200, 256, 96, "#6e5a8a", "#5a4870", "short", arms=[[(-6, 8), (-20, 0), (-34, -6)], [(6, 10), (10, 30)]], lean=-4))
    out.append(jesus_fallen(118, 260, 2))
    out.append(frame_close(7))
    return "".join(out)


def s8():
    out = [frame_open("day", 8), city(180), ground(244)]
    out.append(jesus_carrying(72, 258, 2, cross_back=True))
    # turning, he raises a hand to speak to the women
    out.append(arm([(80, 172), (98, 168), (108, 152)], C["jesus2"]))
    for i, (x, col, vcol) in enumerate(((150, C["woman1"], "#6a4270"), (188, C["woman2"], "#8a5a2a"))):
        out.append(standing(x, 258 + i * 2, 88, col, vcol, "veil", vcol,
                            arms=[[(-4, 8), (-6, 0), (-6, -8)], [(6, 10), (-2, 22)]], lean=-4))
    out.append(kneeling(206, 272, "#2f6a8a", "short", None, [[(-6, 8), (-10, 20)]], -1, 46))
    out.append(frame_close(8))
    return "".join(out)


def s9():
    out = [frame_open("dusk", 9), golgotha(128, 186, 0.5), ground(250, hill=True)]
    out.append(soldier(46, 262, 1, h=96))
    out.append(jesus_fallen(128, 266, 3))
    out.append(frame_close(9))
    return "".join(out)


def s10():
    out = [frame_open("dusk", 10), ground(244, hill=True)]
    # Jesus stands with a white cloth; a soldier holds up the seamless red tunic
    out.append(cross((40, 254), (66, 120), 0.78, 28, 10))
    out.append(robe((104, 170), (102, 252), 22, 22, SKIN, 0.03))
    out.append(robe((103, 204), (102, 236), 26, 30, C["white"], 0.02))
    out.append(head(104, 154, 9.5, "thorns", halo=True))
    out.append(arm([(96, 176), (92, 196), (98, 210)], SKIN, 7))
    out.append(arm([(112, 176), (114, 196), (108, 210)], SKIN, 7))
    out.append(soldier(186, 258, -1, spear=False, arms=[[(-8, 6), (-22, -8), (-30, -18)], [(6, 8), (-12, -6), (-22, -16)]]))
    out.append(path("M140 128 h26 l6 50 h-38Z", C["jesus"], 2))
    # dice
    out.append(path("M140 262h8v8h-8Z M154 266h8v8h-8Z", C["white"], 1.5))
    out.append(circle(144, 266, 1.2, LEAD) + circle(158, 270, 1.2, LEAD))
    out.append(frame_close(10))
    return "".join(out)


def s11():
    out = [frame_open("dusk", 11), ground(232, hill=True)]
    # a soldier kneels beyond the cross with a hammer
    out.append(kneeling(126, 238, C["soldier"], "helmet", None, [[(4, 6), (14, -8), (20, -20)], [(6, 8), (22, 28), (30, 34)]], 1, 62))
    out.append(path("M150 168 l10 -9", "none", 3.5, "#4a3a2a"))
    out.append(path("M155 154 l9 10", "none", 7, C["metal"]))
    # the cross lies on the ground and Jesus is stretched upon it
    out.append(cross((26, 262), (214, 252), 0.76, 34, 12))
    out.append(arm([(170, 254), (169, 226)], SKIN, 7))
    out.append(arm([(170, 258), (172, 286)], SKIN, 7))
    out.append(robe((172, 256), (66, 260), 20, 16, SKIN, 0.02))
    out.append(robe((136, 257), (108, 258), 23, 23, C["white"], 0.01))
    out.append(head(186, 255, 9.5, "thorns", halo=True, tilt=-90))
    out.append(frame_close(11))
    return "".join(out)


def s12():
    out = [frame_open("dark", 12)]
    out.append(circle(196, 112, 16, "#3a2e44", ' stroke="none"'))
    out.append(circle(192, 108, 15, "#8a7a6a", ' stroke="none" opacity=".35"'))
    out.append(ground(248, C["ground2"], hill=True))
    out.append(cross((120, 262), (120, 70), 0.8, 52, 12))
    out.append(path("M108 76h24v13h-24Z", C["white"], 1.5))
    out.append('<text x="120" y="86" text-anchor="middle" font-family="Georgia, serif" font-size="9" font-weight="700" fill="#2a2320" stroke="none">INRI</text>')
    # the crucified Christ
    out.append(arm([(120, 118), (94, 104), (72, 98)], SKIN, 7))
    out.append(arm([(120, 118), (146, 104), (168, 98)], SKIN, 7))
    out.append(robe((120, 114), (121, 196), 20, 16, SKIN, 0.04))
    out.append(robe((120, 160), (121, 182), 24, 26, C["white"], 0.02))
    out.append(arm([(118, 190), (119, 222)], SKIN, 6, False))
    out.append(head(124, 106, 9, "thorns", halo=True, tilt=25))
    # Mary and John at the foot of the cross
    out.append(mary(70, 268, 88, arms=[[(4, 10), (14, 20), (18, 12)], [(-4, 10), (8, 22), (16, 14)]], lean=4))
    out.append(standing(170, 268, 90, C["john"], "#2d5f34", "hair", arms=[[(-4, 10), (-10, 24), (-14, 14)]], lean=-4,
                        mantle="#c9474a"))
    out.append(frame_close(12))
    return "".join(out)


def s13():
    out = [frame_open("dusk", 13), ground(242, hill=True)]
    out.append(cross((120, 250), (120, 70), 0.8, 50, 12))
    # the linen cloth left hanging over the crossbar, and a ladder
    out.append(path("M80 108 Q78 150 86 196 L104 192 Q98 150 106 108Z", C["white"]))
    out.append(path("M150 90 L176 246", "none", 3.2, "#5a4630") + path("M162 90 L188 246", "none", 3.2, "#5a4630"))
    for k in range(7):
        yy = 104 + k * 21
        out.append(path(f"M{_f(150 + (yy - 90) * 0.167)} {yy} h12", "none", 3, "#5a4630"))
    # Mary seated, holding her Son across her lap (a pieta)
    out.append(robe((104, 166), (104, 258), 30, 70, C["mary2"], 0.06))
    out.append(robe((104, 164), (108, 238), 34, 60, C["mary"], 0.12))
    out.append(head(106, 150, 9.5, "veil", C["mary"]))
    out.append(circle(106, 150, 16.5, "none", f' stroke="{C["gold"]}" stroke-width="3"'))
    out.append(arm([(76, 220), (80, 248)], SKIN, 6, False))
    out.append(robe((70, 214), (160, 222), 18, 14, SKIN, 0.02))
    out.append(robe((108, 215), (130, 219), 22, 22, C["white"], 0.02))
    out.append(arm([(158, 222), (168, 252)], SKIN, 6, False))
    out.append(head(60, 206, 9, "thorns", halo=True, tilt=-120))
    out.append(arm([(92, 176), (74, 198), (66, 208)], C["mary"]))
    out.append(arm([(118, 180), (130, 204), (138, 214)], C["mary"]))
    out.append(frame_close(13))
    return "".join(out)


def s14():
    out = [frame_open("night", 14)]
    for x, y in ((40, 110), (70, 96), (186, 104), (210, 132), (160, 88), (52, 150)):
        out.append(circle(x, y, 1.6, "#f4ecd8", ' stroke="none"'))
    out.append(ground(238, C["ground2"]))
    # the rock tomb, with the great stone ready to be rolled across the door
    out.append(path("M24 254 Q26 140 112 136 Q200 140 204 254Z", C["stone"]))
    out.append(path("M62 254 V200 a42 38 0 0 1 84 0 V254Z", "#2a2230"))
    # the body, wrapped in linen, laid inside
    out.append(path("M70 240 q34 -9 70 0 q2 6 -2 9 q-33 4 -66 0 q-4 -4 -2 -9Z", C["white"]))
    out.append(path("M86 238 v10 M100 236 v12 M114 236 v12 M128 238 v10", "none", 1.2, "#b5a684"))
    out.append(circle(178, 238, 32, C["stone2"]))
    out.append(circle(178, 238, 21, "none", ' stroke="#5e5646" stroke-width="2"'))
    # garden plants
    for x, h in ((22, 34), (36, 24), (218, 30)):
        out.append(path(f"M{x} 266 q-8 -{h * 0.6:.0f} 0 -{h} q8 {h * 0.4:.0f} 0 {h}Z", "#3f6a44", 1.5))
    out.append(frame_close(14))
    return "".join(out)


def s0():
    # before the first station: the cross on the hill at daybreak
    out = [frame_open("dusk", 0), rays(120, 128, 11, 120), ground(236, hill=True)]
    out.append(cross((120, 250), (120, 92), 0.76, 40, 12))
    for x, h in ((40, 26), (200, 30), (182, 20)):
        out.append(path(f"M{x} 262 q-7 -{h * 0.6:.0f} 0 -{h} q7 {h * 0.4:.0f} 0 {h}Z", "#3f6a44", 1.5))
    out.append(frame_close(0))
    return "".join(out)


def s15():
    # after the fourteenth station: the stone rolled away, Easter morning
    out = [frame_open("day", 15), rays(120, 190, 13, 150, "#fff3c4"), ground(238, "#7d8a52")]
    out.append(path("M24 254 Q26 140 112 136 Q200 140 204 254Z", C["stone"]))
    out.append(path("M62 254 V200 a42 38 0 0 1 84 0 V254Z", "#3a3240"))
    out.append(path("M76 246 q30 -6 58 0 l-4 6 q-26 3 -50 0Z", C["white"]))
    out.append(circle(206, 240, 30, C["stone2"]))
    out.append(circle(206, 240, 19, "none", ' stroke="#5e5646" stroke-width="2"'))
    for x, h in ((22, 34), (36, 24)):
        out.append(path(f"M{x} 266 q-8 -{h * 0.6:.0f} 0 -{h} q8 {h * 0.4:.0f} 0 {h}Z", "#3f6a44", 1.5))
    for x in (40, 52, 150):
        out.append(circle(x, 268, 3.2, "#f4ecd8", ' stroke="#2a2320" stroke-width="1"') + circle(x, 268, 1.2, C["gold"], ' stroke="none"'))
    out.append(frame_close(15))
    return "".join(out)


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15]


def scene(n):
    return SCENES[n]()


def svg(n, title):
    import html
    return (f'<svg class="st-art" viewBox="0 0 {W} {H}" role="img" aria-labelledby="st-art-{n}">'
            f'<title id="st-art-{n}">{html.escape(title)}</title>{scene(n)}</svg>')
