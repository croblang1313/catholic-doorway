"""Original coloring-page line art and picture icons for the Kids and Families section.

Every drawing is built here from simple shapes (circles, ellipses and hand-placed
curves). Nothing is traced or copied from existing artwork.

Coloring pages use three kinds of shape, styled by the page CSS:
  .r  a closed region that a child can tap to fill (white with a dark outline)
  .l  a line only (folds, faces, rays); never filled and ignores taps
  .k  a small solid dot (eyes)
Regions are drawn back to front, so a tap fills the topmost shape under the finger.
"""
import math

W, H = 400, 520


def _f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def _xy(x, y):
    return f"{_f(x)} {_f(y)}"


def R(d):
    return f'<path class="r" d="{d}"/>'


def L(d, w=None):
    s = f' style="stroke-width:{w}"' if w else ""
    return f'<path class="l" d="{d}"{s}/>'


def C(x, y, r):
    return f'<circle class="r" cx="{_f(x)}" cy="{_f(y)}" r="{_f(r)}"/>'


def E(x, y, rx, ry, rot=0):
    t = f' transform="rotate({_f(rot)} {_f(x)} {_f(y)})"' if rot else ""
    return f'<ellipse class="r" cx="{_f(x)}" cy="{_f(y)}" rx="{_f(rx)}" ry="{_f(ry)}"{t}/>'


def K(x, y, r=2.8):
    return f'<circle class="k" cx="{_f(x)}" cy="{_f(y)}" r="{_f(r)}"/>'


def P(pts):
    return R("M" + " L".join(_xy(x, y) for x, y in pts) + "Z")


def rect(x, y, w, h, rx=0):
    return f'<rect class="r" x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" rx="{_f(rx)}"/>'


def sky():
    return rect(0, 0, W, H)


def hill(y=400, bump=-40, y2=None):
    y2 = y if y2 is None else y2
    return R(f"M0 {_f(y)} Q200 {_f(min(y, y2) + bump)} 400 {_f(y2)} L400 520 L0 520Z")


def sun(x, y, r=30, rays=10):
    out = [C(x, y, r)]
    for i in range(rays):
        a = 2 * math.pi * i / rays
        out.append(L(f"M{_xy(x + math.cos(a) * (r + 8), y + math.sin(a) * (r + 8))} L{_xy(x + math.cos(a) * (r + 22), y + math.sin(a) * (r + 22))}"))
    return "".join(out)


def cloud(x, y, s=1):
    return R(f"M{_xy(x - 40 * s, y + 12 * s)} Q{_xy(x - 52 * s, y - 8 * s)} {_xy(x - 28 * s, y - 10 * s)} "
             f"Q{_xy(x - 22 * s, y - 34 * s)} {_xy(x, y - 26 * s)} Q{_xy(x + 22 * s, y - 40 * s)} {_xy(x + 32 * s, y - 12 * s)} "
             f"Q{_xy(x + 54 * s, y - 8 * s)} {_xy(x + 44 * s, y + 12 * s)}Z")


def star(x, y, r, points=5, inner=0.45):
    pts = []
    for i in range(points * 2):
        a = -math.pi / 2 + math.pi * i / points
        rr = r if i % 2 == 0 else r * inner
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    return P(pts)


def flower(x, y, s=1, stem=40):
    out = [L(f"M{_xy(x, y)} L{_xy(x, y + stem * s)}"),
           E(x + 9 * s, y + stem * s * 0.6, 9 * s, 4 * s, -30)]
    for i in range(5):
        a = 2 * math.pi * i / 5 - math.pi / 2
        out.append(C(x + math.cos(a) * 9 * s, y + math.sin(a) * 9 * s, 7 * s))
    out.append(C(x, y, 5.5 * s))
    return "".join(out)


def rose(x, y, s=1, leaves=True):
    out = []
    if leaves:
        out += [E(x - 15 * s, y + 10 * s, 10 * s, 5 * s, 30), E(x + 15 * s, y + 10 * s, 10 * s, 5 * s, -30)]
    out.append(C(x, y, 13 * s))
    out.append(L(f"M{_xy(x - 5 * s, y - 2 * s)} Q{_xy(x, y - 9 * s)} {_xy(x + 6 * s, y - 2 * s)} Q{_xy(x + 5 * s, y + 7 * s)} {_xy(x - 3 * s, y + 6 * s)} Q{_xy(x - 9 * s, y + 2 * s)} {_xy(x - 6 * s, y - 6 * s)}"))
    return "".join(out)


def bird(x, y, s=1, flip=False):
    f = -1 if flip else 1
    return (E(x, y, 16 * s, 10 * s)
            + C(x + f * 14 * s, y - 8 * s, 8 * s)
            + P([(x + f * 21 * s, y - 10 * s), (x + f * 30 * s, y - 7 * s), (x + f * 21 * s, y - 4 * s)])
            + R(f"M{_xy(x - f * 4 * s, y - 2 * s)} Q{_xy(x - f * 16 * s, y - 22 * s)} {_xy(x - f * 22 * s, y - 4 * s)} Q{_xy(x - f * 12 * s, y + 2 * s)} {_xy(x - f * 4 * s, y - 2 * s)}Z")
            + P([(x - f * 15 * s, y - 1 * s), (x - f * 28 * s, y + 3 * s), (x - f * 15 * s, y + 7 * s)])
            + K(x + f * 16 * s, y - 10 * s, 1.8 * s))


def flying(x, y, s=1):
    return L(f"M{_xy(x - 14 * s, y)} Q{_xy(x - 7 * s, y - 9 * s)} {_xy(x, y)} Q{_xy(x + 7 * s, y - 9 * s)} {_xy(x + 14 * s, y)}")


def sheep(x, y, s=1, flip=False):
    f = -1 if flip else 1
    out = [rect(x - 22 * s, y + 10 * s, 7 * s, 22 * s, 3 * s), rect(x + 14 * s, y + 10 * s, 7 * s, 22 * s, 3 * s)]
    puffs = [(-22, 0), (-10, -12), (6, -13), (20, -2), (8, 10), (-10, 10)]
    body = "M" + " ".join(
        f"{'' if i == 0 else 'A14 14 0 0 1 '}{_xy(x + dx * s, y + dy * s)}" for i, (dx, dy) in enumerate(puffs + [puffs[0]]))
    out.append(R(body + "Z"))
    out.append(E(x + f * 30 * s, y - 6 * s, 10 * s, 13 * s, f * 20))
    out.append(E(x + f * 22 * s, y - 16 * s, 7 * s, 3.5 * s, f * -20))
    out.append(K(x + f * 33 * s, y - 9 * s, 1.9 * s))
    return "".join(out)


def fish(x, y, s=1, flip=False):
    f = -1 if flip else 1
    return (P([(x - f * 20 * s, y), (x - f * 34 * s, y - 11 * s), (x - f * 34 * s, y + 11 * s)])
            + R(f"M{_xy(x - f * 22 * s, y)} Q{_xy(x, y - 18 * s)} {_xy(x + f * 24 * s, y)} Q{_xy(x, y + 18 * s)} {_xy(x - f * 22 * s, y)}Z")
            + L(f"M{_xy(x + f * 10 * s, y - 9 * s)} Q{_xy(x + f * 5 * s, y)} {_xy(x + f * 10 * s, y + 9 * s)}")
            + K(x + f * 15 * s, y - 3 * s, 1.8 * s))


def flame(x, y, s=1):
    return R(f"M{_xy(x, y + 12 * s)} Q{_xy(x - 11 * s, y + 10 * s)} {_xy(x - 8 * s, y - 2 * s)} Q{_xy(x - 4 * s, y - 10 * s)} {_xy(x, y - 22 * s)} "
             f"Q{_xy(x + 4 * s, y - 10 * s)} {_xy(x + 8 * s, y - 2 * s)} Q{_xy(x + 11 * s, y + 10 * s)} {_xy(x, y + 12 * s)}Z")


def candle(x, y, w, h):
    return rect(x - w / 2, y, w, h, 3) + flame(x, y - 14, 0.9) + L(f"M{_xy(x, y)} L{_xy(x, y - 4)}")


def cross(x, y, h, w=None, t=None, arm=0.3):
    w = w or h * 0.6
    t = t or h * 0.14
    ay = y + h * arm
    return P([(x - t / 2, y), (x + t / 2, y), (x + t / 2, ay), (x + w / 2, ay), (x + w / 2, ay + t), (x + t / 2, ay + t),
              (x + t / 2, y + h), (x - t / 2, y + h), (x - t / 2, ay + t), (x - w / 2, ay + t), (x - w / 2, ay), (x - t / 2, ay)])


def lily(x, y, s=1):
    return (L(f"M{_xy(x, y)} Q{_xy(x - 4 * s, y + 40 * s)} {_xy(x, y + 80 * s)}")
            + E(x - 12 * s, y + 52 * s, 14 * s, 5 * s, 55) + E(x + 11 * s, y + 62 * s, 14 * s, 5 * s, -55)
            + R(f"M{_xy(x, y + 4 * s)} Q{_xy(x - 24 * s, y - 10 * s)} {_xy(x - 22 * s, y - 34 * s)} Q{_xy(x - 10 * s, y - 24 * s)} {_xy(x - 8 * s, y - 34 * s)} "
                f"Q{_xy(x, y - 22 * s)} {_xy(x + 8 * s, y - 34 * s)} Q{_xy(x + 10 * s, y - 24 * s)} {_xy(x + 22 * s, y - 34 * s)} Q{_xy(x + 24 * s, y - 10 * s)} {_xy(x, y + 4 * s)}Z")
            + L(f"M{_xy(x, y - 4 * s)} L{_xy(x - 3 * s, y - 24 * s)}M{_xy(x, y - 4 * s)} L{_xy(x + 4 * s, y - 24 * s)}"))


def shamrock(x, y, s=1):
    out = [L(f"M{_xy(x, y + 6 * s)} Q{_xy(x + 4 * s, y + 22 * s)} {_xy(x + 12 * s, y + 32 * s)}", 4)]
    for a in (-90, 20, 160):
        r = math.radians(a)
        cx, cy = x + math.cos(r) * 11 * s, y + math.sin(r) * 11 * s
        px, py = -math.sin(r), math.cos(r)
        # heart-shaped leaf: two lobes, point toward the center
        out.append(R(f"M{_xy(x, y)} C{_xy(cx + px * 14 * s, cy + py * 14 * s)} {_xy(cx + math.cos(r) * 16 * s + px * 10 * s, cy + math.sin(r) * 16 * s + py * 10 * s)} {_xy(cx + math.cos(r) * 10 * s, cy + math.sin(r) * 10 * s)} "
                     f"C{_xy(cx + math.cos(r) * 16 * s - px * 10 * s, cy + math.sin(r) * 16 * s - py * 10 * s)} {_xy(cx - px * 14 * s, cy - py * 14 * s)} {_xy(x, y)}Z"))
    return "".join(out)


def sleeve(sx, sy, hx, hy, w1=26, w2=16, hand=9):
    dx, dy = hx - sx, hy - sy
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    px, py = -uy, ux
    pts = [(sx + px * w1 / 2, sy + py * w1 / 2), (hx + px * w2 / 2, hy + py * w2 / 2),
           (hx - px * w2 / 2, hy - py * w2 / 2), (sx - px * w1 / 2, sy - py * w1 / 2)]
    out = ""
    if hand:
        out += C(hx + ux * hand * 0.7, hy + uy * hand * 0.7, hand)
    return out + P(pts)


def face(x, y, s=1, smile=True):
    out = K(x - 9 * s, y - 2 * s, 2.6 * s) + K(x + 9 * s, y - 2 * s, 2.6 * s)
    if smile:
        out += L(f"M{_xy(x - 8 * s, y + 9 * s)} Q{_xy(x, y + 15 * s)} {_xy(x + 8 * s, y + 9 * s)}")
    return out


def person(x, y, s=1, arms="pray", halo=True, head_kind="hair", beard=False, length=190, hem=60, robe=True,
           belt=None, hands=True):
    """A robed figure with its head centered at (x, y).
    arms: "pray", "none" or a pair of hand points ((lx, ly), (rx, ry))."""
    out = []
    if halo:
        out.append(C(x, y - 4 * s, 38 * s))
    if head_kind in ("veil", "hood", "nun"):
        out.append(R(f"M{_xy(x - 36 * s, y + 40 * s)} Q{_xy(x - 44 * s, y - 38 * s)} {_xy(x, y - 36 * s)} "
                     f"Q{_xy(x + 44 * s, y - 38 * s)} {_xy(x + 36 * s, y + 40 * s)}Z"))
    yh = y + 20 * s + length * s
    if robe:
        out += [E(x - 20 * s, yh + 4 * s, 14 * s, 7 * s), E(x + 20 * s, yh + 4 * s, 14 * s, 7 * s)]
        out.append(R(f"M{_xy(x - 28 * s, y + 22 * s)} Q{_xy(x - 50 * s, y + 120 * s)} {_xy(x - hem * s, yh)} "
                     f"Q{_xy(x, yh + 12 * s)} {_xy(x + hem * s, yh)} Q{_xy(x + 50 * s, y + 120 * s)} {_xy(x + 28 * s, y + 22 * s)} "
                     f"Q{_xy(x, y + 14 * s)} {_xy(x - 28 * s, y + 22 * s)}Z"))
        if belt:
            by = y + 20 * s + belt * s
            out.append(L(f"M{_xy(x - 40 * s, by)} Q{_xy(x, by + 8 * s)} {_xy(x + 40 * s, by)}"))
    if head_kind == "nun":  # white wimple around the face
        out.append(R(f"M{_xy(x - 30 * s, y + 4 * s)} Q{_xy(x - 32 * s, y - 30 * s)} {_xy(x, y - 30 * s)} Q{_xy(x + 32 * s, y - 30 * s)} {_xy(x + 30 * s, y + 4 * s)} "
                     f"Q{_xy(x + 34 * s, y + 46 * s)} {_xy(x, y + 48 * s)} Q{_xy(x - 34 * s, y + 46 * s)} {_xy(x - 30 * s, y + 4 * s)}Z"))
    if arms == "pray":
        out.append(sleeve(x - 24 * s, y + 42 * s, x - 7 * s, y + 92 * s, 24 * s, 18 * s, 0))
        out.append(sleeve(x + 24 * s, y + 42 * s, x + 7 * s, y + 92 * s, 24 * s, 18 * s, 0))
        if hands:
            out.append(R(f"M{_xy(x, y + 62 * s)} Q{_xy(x - 10 * s, y + 80 * s)} {_xy(x - 8 * s, y + 92 * s)} L{_xy(x + 8 * s, y + 92 * s)} Q{_xy(x + 10 * s, y + 80 * s)} {_xy(x, y + 62 * s)}Z"))
    elif arms != "none":
        (lx, ly), (rx, ry) = arms
        out.append(sleeve(x - 24 * s, y + 42 * s, lx, ly, 24 * s, 17 * s, 9 * s if hands else 0))
        out.append(sleeve(x + 24 * s, y + 42 * s, rx, ry, 24 * s, 17 * s, 9 * s if hands else 0))
    out.append(C(x, y, 24 * s))
    if head_kind == "hair":
        out.append(R(f"M{_xy(x - 24 * s, y - 1 * s)} Q{_xy(x - 27 * s, y - 31 * s)} {_xy(x, y - 29 * s)} Q{_xy(x + 27 * s, y - 31 * s)} {_xy(x + 24 * s, y - 1 * s)} "
                     f"Q{_xy(x + 14 * s, y - 16 * s)} {_xy(x, y - 15 * s)} Q{_xy(x - 14 * s, y - 16 * s)} {_xy(x - 24 * s, y - 1 * s)}Z"))
    elif head_kind == "long":
        out.append(R(f"M{_xy(x - 24 * s, y + 26 * s)} Q{_xy(x - 34 * s, y - 32 * s)} {_xy(x, y - 30 * s)} Q{_xy(x + 34 * s, y - 32 * s)} {_xy(x + 24 * s, y + 26 * s)} "
                     f"L{_xy(x + 18 * s, y + 8 * s)} Q{_xy(x + 20 * s, y - 14 * s)} {_xy(x, y - 15 * s)} Q{_xy(x - 20 * s, y - 14 * s)} {_xy(x - 18 * s, y + 8 * s)}Z"))
    elif head_kind == "mitre":
        out.append(R(f"M{_xy(x - 20 * s, y - 14 * s)} L{_xy(x - 22 * s, y - 56 * s)} Q{_xy(x - 12 * s, y - 70 * s)} {_xy(x, y - 82 * s)} "
                     f"Q{_xy(x + 12 * s, y - 70 * s)} {_xy(x + 22 * s, y - 56 * s)} L{_xy(x + 20 * s, y - 14 * s)} Q{_xy(x, y - 20 * s)} {_xy(x - 20 * s, y - 14 * s)}Z"))
        out.append(L(f"M{_xy(x, y - 62 * s)} L{_xy(x, y - 34 * s)}M{_xy(x - 9 * s, y - 50 * s)} L{_xy(x + 9 * s, y - 50 * s)}"))
    elif head_kind in ("veil", "hood"):
        out.append(L(f"M{_xy(x - 22 * s, y - 8 * s)} Q{_xy(x, y - 22 * s)} {_xy(x + 22 * s, y - 8 * s)}"))
    if beard:
        out.append(R(f"M{_xy(x - 22 * s, y + 6 * s)} Q{_xy(x - 20 * s, y + 40 * s)} {_xy(x, y + 44 * s)} Q{_xy(x + 20 * s, y + 40 * s)} {_xy(x + 22 * s, y + 6 * s)} "
                     f"Q{_xy(x + 12 * s, y + 20 * s)} {_xy(x, y + 19 * s)} Q{_xy(x - 12 * s, y + 20 * s)} {_xy(x - 22 * s, y + 6 * s)}Z"))
        out.append(K(x - 9 * s, y - 3 * s, 2.6 * s) + K(x + 9 * s, y - 3 * s, 2.6 * s)
                   + L(f"M{_xy(x - 6 * s, y + 11 * s)} Q{_xy(x, y + 15 * s)} {_xy(x + 6 * s, y + 11 * s)}"))
    else:
        out.append(face(x, y, s))
    return "".join(out)


def staff(x, y1, y2, curl=True):
    out = rect(x - 5, y1, 10, y2 - y1, 4)
    if curl:
        out += R(f"M{_xy(x - 5, y1 + 4)} Q{_xy(x - 8, y1 - 34)} {_xy(x + 18, y1 - 36)} Q{_xy(x + 40, y1 - 30)} {_xy(x + 32, y1 - 10)} "
                 f"Q{_xy(x + 24, y1 + 2)} {_xy(x + 16, y1 - 8)} Q{_xy(x + 26, y1 - 14)} {_xy(x + 22, y1 - 22)} Q{_xy(x + 8, y1 - 28)} {_xy(x + 5, y1 + 4)}Z")
    return out


def gift(x, y, w, h):
    return (rect(x, y, w, h, 3) + rect(x - 4, y - 12, w + 8, 14, 3)
            + L(f"M{_xy(x + w / 2, y - 12)} L{_xy(x + w / 2, y + h)}")
            + R(f"M{_xy(x + w / 2, y - 12)} Q{_xy(x + w / 2 - 22, y - 34)} {_xy(x + w / 2 - 8, y - 32)} Q{_xy(x + w / 2 - 2, y - 26)} {_xy(x + w / 2, y - 12)}Z")
            + R(f"M{_xy(x + w / 2, y - 12)} Q{_xy(x + w / 2 + 22, y - 34)} {_xy(x + w / 2 + 8, y - 32)} Q{_xy(x + w / 2 + 2, y - 26)} {_xy(x + w / 2, y - 12)}Z"))


def waves(y, n=6, amp=10):
    d = f"M0 {_f(y)}"
    step = W / n
    for i in range(n):
        d += f" Q{_xy(step * i + step / 2, y - amp * 2)} {_xy(step * (i + 1), y)}"
    return R(d + " L400 520 L0 520Z")


# ---------------------------------------------------------------- the coloring pages

def francis():
    return [sky(), sun(330, 70), cloud(90, 80), hill(410),
            L("M40 120 Q48 112 56 120 Q64 112 72 120"), flying(260, 60), flying(300, 130, 0.8),
            person(200, 175, 1.1, arms=((118, 200), (290, 250)), head_kind="hood", belt=86),
            L("M180 290 L176 330 M176 330 L170 352 M182 336 L186 356"),
            bird(110, 178, 0.9), bird(302, 238, 0.8, flip=True), bird(80, 455, 1.0), bird(318, 450, 0.9, flip=True),
            flower(40, 420), flower(150, 470, 0.9), flower(250, 480, 0.8), flower(360, 418)]


def therese():
    out = [sky()]
    for x, y in ((50, 60), (350, 70), (40, 260), (360, 250), (60, 440), (340, 450), (120, 30), (280, 30)):
        out.append(rose(x, y, 1.1))
    out.append(R("M0 470 Q200 450 400 470 L400 520 L0 520Z"))
    out.append(person(200, 150, 1.15, arms=((180, 268), (222, 268)), head_kind="nun", length=200, hands=True))
    out.append(cross(200, 205, 70, 40, 9))
    out += [rose(176, 270, 0.9), rose(206, 280, 0.9), rose(232, 262, 0.85)]
    return out


def nicholas():
    out = [sky()]
    for x, y, r in ((60, 60, 14), (130, 40, 9), (290, 50, 11), (350, 110, 15), (40, 170, 9), (370, 220, 10)):
        out.append(star(x, y, r))
    out += [R("M0 450 Q200 430 400 450 L400 520 L0 520Z"),
            staff(108, 150, 445), person(200, 165, 1.15, arms=((112, 260), (296, 150)), head_kind="mitre", beard=True, length=205, hem=68),
            R("M152 200 L200 300 L248 200 Q200 214 152 200Z"),
            gift(40, 405, 56, 46), gift(300, 410, 66, 42), C(260, 470, 12), C(286, 478, 12), C(312, 486, 12)]
    return out


def juan_diego():
    out = [sky(), sun(70, 70, 26), hill(380, -70, 420), cloud(310, 70, 0.9),
           person(200, 140, 1.1, arms=((120, 272), (280, 272)), head_kind="hair", length=210),
           R("M124 250 Q118 300 130 360 Q200 378 270 360 Q282 300 276 250 Q200 266 124 250Z")]
    for x, y in ((156, 286), (194, 296), (234, 284), (172, 326), (214, 330), (250, 320), (140, 322)):
        out.append(rose(x, y, 0.95, leaves=False))
    out += [L("M210 140 L216 150")]
    out += [rose(60, 440), rose(110, 470, 0.9), rose(300, 470, 0.9), rose(350, 440)]
    return out


def patrick():
    return [sky(), cloud(80, 70), cloud(320, 100, 0.8), hill(370, -60, 400), R("M0 440 Q120 410 260 450 Q330 470 400 440 L400 520 L0 520Z"),
            staff(300, 150, 450),
            person(200, 160, 1.15, arms=((120, 120), (296, 260)), head_kind="hair", beard=True, length=205, hem=66),
            R("M150 196 L200 250 L250 196 Q200 210 150 196Z"),
            shamrock(118, 96, 1.4), shamrock(60, 470), shamrock(150, 488, 0.8), shamrock(350, 480)]


def joseph():
    return [sky(), R("M0 380 L400 380 L400 520 L0 520Z"),
            rect(230, 330, 160, 18, 3), rect(240, 348, 12, 90), rect(368, 348, 12, 90),
            P([(250, 318), (330, 318), (330, 330), (250, 330)]), R("M338 300 L354 300 L354 330 L338 330Z"), rect(344, 286, 30, 14, 3),
            rect(30, 400, 120, 14, 2), rect(40, 418, 130, 14, 2),
            person(140, 150, 1.1, arms=((100, 250), (196, 200)), head_kind="hair", beard=True, length=210),
            L("M100 250 Q94 190 104 130", 4), C(104, 120, 9), E(92, 128, 10, 5, 30), E(116, 128, 10, 5, -30), E(104, 108, 5, 10),
            person(285, 230, 0.75, arms=((240, 300), (330, 296)), head_kind="hair", length=165, hem=48)]


def noah():
    out = [sky()]
    for i, r in enumerate((190, 172, 154, 136, 118, 100)):
        out.append(R(f"M{_f(200 - r)} 250 A{_f(r)} {_f(r)} 0 0 1 {_f(200 + r)} 250Z"))
    out += [cloud(60, 250, 1), cloud(340, 250, 1),
            rect(140, 230, 120, 70, 4), R("M128 232 L200 190 L272 232Z"), C(170, 262, 14), C(230, 262, 14),
            C(170, 260, 9), E(161, 250, 4, 6), E(179, 250, 4, 6), E(230, 262, 8, 10),
            R("M60 300 L340 300 L310 370 Q200 382 90 370Z"), L("M75 324 L325 324 M86 348 L314 348"),
            waves(380, 5, 12), L("M40 430 Q60 420 80 430 M220 470 Q240 460 260 470 M300 420 Q320 410 340 420"),
            bird(320, 160, 0.9, flip=True), L("M290 166 Q284 176 276 178", 3), E(280, 182, 6, 3, 20)]
    return out


def jonah():
    return [sky(), sun(340, 70, 28), cloud(90, 90),
            R("M300 380 Q330 300 400 300 L400 520 L300 520Z"),
            waves(360, 5, 10),
            R("M40 390 Q60 300 170 300 Q270 300 280 380 Q270 440 170 450 Q80 450 40 390Z"),
            R("M40 390 Q10 350 2 320 Q24 340 40 350 Q30 330 30 300 Q54 330 56 372Z"),
            R("M70 410 Q170 440 270 400 Q250 440 170 450 Q90 450 70 410Z"),
            L("M100 420 L240 418 M110 432 L230 430"), K(230, 345, 4),
            L("M268 390 Q240 396 220 392"), L("M160 300 Q150 270 162 250 M160 300 Q172 268 190 262 M160 300 Q146 284 128 278"),
            person(352, 220, 0.8, arms="pray", head_kind="hair", beard=True, length=105, hem=42, halo=False)]


def nativity():
    out = [sky(), star(200, 46, 22, 8, 0.4)]
    for a in range(8):
        r = math.radians(a * 45 + 22)
        out.append(L(f"M{_xy(200 + math.cos(r) * 28, 46 + math.sin(r) * 28)} L{_xy(200 + math.cos(r) * 44, 46 + math.sin(r) * 44)}"))
    out += [R("M30 170 L200 90 L370 170 L350 182 L200 112 L50 182Z"), rect(64, 176, 16, 280), rect(320, 176, 16, 280),
            R("M0 440 L400 440 L400 520 L0 520Z"),
            L("M20 470 L40 458 M60 480 L74 466 M330 476 L350 462 M370 486 L384 472"),
            person(110, 270, 0.85, arms=((150, 358), (162, 344)), head_kind="veil", length=150, hem=56),
            person(300, 230, 0.95, arms=((262, 330), (342, 300)), head_kind="hair", beard=True, length=190, hem=58),
            staff(350, 260, 440, curl=False),
            R("M155 390 L245 390 L232 430 L168 430Z"), L("M168 430 L150 456 M232 430 L250 456 M175 430 L190 456 M225 430 L210 456"),
            C(200, 368, 26), E(206, 384, 34, 14), C(180, 378, 12), face(180, 378, 0.45),
            L("M160 390 Q170 380 180 392 Q192 380 204 392 Q216 380 228 392 Q236 382 244 390"),
            sheep(60, 470, 0.8)]
    return out


def good_shepherd():
    return [sky(), sun(330, 70, 26), cloud(80, 70, 0.9), hill(360, -50, 380), R("M0 450 Q200 420 400 450 L400 520 L0 520Z"),
            staff(96, 140, 470),
            person(200, 175, 1.1, arms=((136, 200), (266, 196)), head_kind="long", beard=True, length=205, hem=62, halo=False),
            sheep(180, 194, 1.6),
            person(200, 175, 1.1, arms="none", head_kind="long", beard=True, robe=False, halo=False),
            sheep(80, 470, 0.9), sheep(320, 466, 1.0, flip=True), flower(270, 492, 0.7, 20), flower(30, 500, 0.7, 20)]


def loaves():
    out = [sky(), sun(330, 70, 26), hill(300, -40, 320),
           R("M20 400 L380 400 L360 500 L40 500Z"), L("M60 420 L340 420"),
           R("M80 300 Q200 330 320 300 L296 420 Q200 440 104 420Z"),
           L("M92 340 Q200 366 308 340 M98 380 Q200 404 302 380 M140 316 L150 428 M200 322 L200 434 M260 316 L250 428")]
    for x, y, rx in ((130, 288, 34), (200, 278, 38), (270, 288, 34), (165, 262, 32), (238, 262, 32)):
        out += [E(x, y, rx, 18), L(f"M{_xy(x - 12, y - 8)} L{_xy(x - 4, y + 6)} M{_xy(x + 4, y - 9)} L{_xy(x + 12, y + 5)}")]
    out += [fish(110, 462, 1.2), fish(290, 462, 1.2, flip=True)]
    return out


def altar():
    return [sky(), R("M120 40 Q200 0 280 40 L280 250 L120 250Z"), L("M200 20 L200 250 M120 140 L280 140"),
            R("M0 420 L400 420 L400 520 L0 520Z"), L("M0 470 L400 470 M100 420 L80 520 M200 420 L200 520 M300 420 L320 520"),
            rect(40, 300, 320, 120, 4), R("M60 300 L340 300 L330 400 L70 400Z"), cross(200, 315, 70, 44, 12),
            rect(30, 290, 340, 14, 4),
            candle(70, 210, 18, 80), candle(330, 210, 18, 80),
            R("M168 210 Q170 256 200 262 Q230 256 232 210Z"), rect(194, 262, 12, 16), E(200, 284, 30, 8),
            C(200, 170, 26), L("M186 170 L214 170 M200 156 L200 184"),
            L("M200 132 L200 116 M170 142 L160 130 M230 142 L240 130 M160 170 L144 170 M240 170 L256 170")]


def ambo():
    out = [sky(), R("M0 430 L400 430 L400 520 L0 520Z"),
           R("M150 230 L250 230 L240 430 L160 430Z"), rect(130, 420, 140, 18, 3), cross(200, 280, 70, 40, 10),
           R("M200 236 L110 210 L120 170 L200 190Z"), R("M200 236 L290 210 L280 170 L200 190Z"),
           L("M130 186 L190 200 M128 198 L188 212 M210 200 L270 186 M212 212 L272 198"),
           candle(330, 260, 22, 170), rect(310, 430, 40, 10, 2)]
    out += [L("M200 160 L200 120 M170 166 L150 132 M230 166 L250 132 M144 180 L110 160 M256 180 L290 160")]
    out += [bird(200, 70, 1.4)]
    return out


def advent_wreath():
    out = [sky(), star(70, 60, 14), star(330, 60, 14), star(200, 40, 10),
           R("M0 430 L400 430 L400 520 L0 520Z"),
           R("M40 380 A160 60 0 1 0 360 380 A160 60 0 1 0 40 380Z M100 380 A100 32 0 1 1 300 380 A100 32 0 1 1 100 380Z")]
    for i in range(14):
        a = 2 * math.pi * i / 14
        out.append(E(200 + math.cos(a) * 130, 380 + math.sin(a) * 47, 22, 9, math.degrees(a) + 90))
    for i in range(7):
        a = 2 * math.pi * i / 7 + 0.2
        out.append(C(200 + math.cos(a) * 130, 380 + math.sin(a) * 47, 7))
    out += [candle(110, 250, 30, 130), candle(160, 230, 30, 140), candle(240, 230, 30, 140), candle(290, 250, 30, 130),
            R("M200 430 Q170 460 150 480 Q176 476 186 462 Q190 490 200 500 Q210 490 214 462 Q224 476 250 480 Q230 460 200 430Z"),
            C(200, 430, 10)]
    return out


def lent_cross():
    out = [sky(), R("M0 400 Q200 300 400 400 L400 520 L0 520Z")]
    for a in range(-80, 81, 20):
        r = math.radians(a - 90)
        out.append(L(f"M{_xy(200 + math.cos(r) * 150, 150 + math.sin(r) * 150)} L{_xy(200 + math.cos(r) * 190, 150 + math.sin(r) * 190)}"))
    out += [cross(200, 60, 300, 200, 30, 0.22),
            R("M112 122 Q200 190 288 122 L288 140 Q200 210 112 140Z"),
            R("M112 122 L94 128 L100 210 L120 200 L126 140Z"), R("M288 122 L306 128 L300 210 L280 200 L274 140Z"),
            R("M170 300 A30 12 0 1 0 230 300 A30 12 0 1 0 170 300Z M182 300 A18 6 0 1 1 218 300 A18 6 0 1 1 182 300Z"),
            L("M178 292 L172 284 M196 290 L194 280 M214 292 L220 283 M228 302 L238 298 M172 306 L162 310"),
            R("M40 470 Q50 430 60 470Z"), R("M340 460 Q352 420 362 460Z"), L("M30 480 L80 480 M330 470 L380 470")]
    return out


def easter():
    out = [sky(), sun(110, 140, 40, 12),
           R("M150 120 Q250 60 380 140 L400 160 L400 420 L150 420Z"),
           R("M180 420 L180 260 Q240 200 300 260 L300 420Z"),
           C(330, 360, 62), L("M300 340 L330 360 L350 334 M330 360 L340 400"),
           R("M0 400 Q200 380 400 410 L400 520 L0 520Z"),
           lily(70, 390, 0.9), lily(140, 410, 0.8), lily(250, 420, 0.75)]
    out += [E(330, 470, 18, 12, -20), E(354, 470, 18, 12, 20), L("M342 458 L342 482 M342 458 L336 446 M342 458 L348 446")]
    return out


def pentecost():
    out = [sky()]
    for a in range(0, 360, 30):
        r = math.radians(a)
        out.append(L(f"M{_xy(200 + math.cos(r) * 70, 110 + math.sin(r) * 70)} L{_xy(200 + math.cos(r) * 100, 110 + math.sin(r) * 100)}"))
    out += [R("M200 140 Q160 110 90 120 Q130 90 170 96 Q120 60 110 30 Q170 50 196 100Z"),
            R("M200 140 Q240 110 310 120 Q270 90 230 96 Q280 60 290 30 Q230 50 204 100Z"),
            E(200, 118, 20, 34), C(200, 82, 16), P([(194, 66), (206, 66), (200, 54)]), K(194, 80, 2.2), K(206, 80, 2.2),
            R("M186 150 L200 182 L214 150Z"),
            R("M0 470 L400 470 L400 520 L0 520Z")]
    for i, x in enumerate((60, 130, 200, 270, 340)):
        y = 380 if i % 2 == 0 else 360
        out += [R(f"M{_xy(x - 38, 470)} Q{_xy(x - 34, y + 40)} {_xy(x, y + 34)} Q{_xy(x + 34, y + 40)} {_xy(x + 38, 470)}Z"),
                C(x, y, 24), face(x, y, 0.8), flame(x, y - 48, 1.2)]
    return out


# id: drawing function, group
PAGES = [("francis", francis, "saints"), ("therese", therese, "saints"), ("nicholas", nicholas, "saints"),
         ("juan-diego", juan_diego, "saints"), ("patrick", patrick, "saints"), ("joseph", joseph, "saints"),
         ("noah", noah, "bible"), ("jonah", jonah, "bible"), ("nativity", nativity, "bible"),
         ("good-shepherd", good_shepherd, "bible"), ("loaves", loaves, "bible"),
         ("altar", altar, "mass"), ("ambo", ambo, "mass"),
         ("advent-wreath", advent_wreath, "seasons"), ("lent-cross", lent_cross, "seasons"),
         ("easter", easter, "seasons"), ("pentecost", pentecost, "seasons")]


def coloring_svg(pid, title):
    fn = dict((p, f) for p, f, _ in PAGES)[pid]
    return (f'<svg class="cpage" viewBox="0 0 {W} {H}" role="img" aria-label="{title}" data-page="{pid}" '
            f'xmlns="http://www.w3.org/2000/svg">{"".join(fn())}</svg>')


# ---------------------------------------------------------------- small color icons for the kids' Mass guide

INK = "#2a2320"


def _i(body):
    return (f'<svg class="kicon" viewBox="0 0 120 120" aria-hidden="true" focusable="false">'
            f'<circle cx="60" cy="60" r="56" fill="var(--kid-bg, #f3ecdd)"/>{body}</svg>')


def _p(d, fill, sw=3):
    return f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>'


ICONS = {
    "cross": _i(_p("M52 20h16v24h22v16H68v42H52V60H30V44h22z", "#e2b64a")),
    "sorry": _i(_p("M60 96C30 76 22 58 30 44c8-14 24-12 30 2 6-14 22-16 30-2 8 14 0 32-30 52z", "#d4646a")
                + _p("M44 52l32 14M76 52L44 66", "none", 3)),
    "glory": _i(_p("M44 82a10 8 0 1 1-1-6V30l40-8v48a10 8 0 1 1-1-6V36l-38 8", "#6a3f8a") + _p("M86 16l3 7 7 1-5 5 1 7-6-4-6 4 1-7-5-5 7-1z", "#e2b64a", 2)),
    "book": _i(_p("M60 38c-10-8-24-8-36-4v52c12-4 26-4 36 4 10-8 24-8 36-4V34c-12-4-26-4-36 4z", "#ffffff")
               + _p("M60 38v52", "none") + _p("M32 48h18M32 58h18M32 68h14M70 48h18M70 58h18M70 68h14", "none", 2.4)),
    "gospel": _i(_p("M34 30h52v62H34z", "#a8322d") + _p("M60 42v38M48 54h24", "none", 4) + _p("M20 96l10-30 10 30zM80 96l10-30 10 30z", "#e2b64a", 2.4)),
    "homily": _i(_p("M22 30h76a6 6 0 0 1 6 6v36a6 6 0 0 1-6 6H54l-18 16V78H22a6 6 0 0 1-6-6V36a6 6 0 0 1 6-6z", "#ffffff")
                 + _p("M60 40c-4-4-12-2-12 5 0 8 12 14 12 14s12-6 12-14c0-7-8-9-12-5z", "#d4646a", 2.4)),
    "gifts": _i(_p("M20 78c0-14 14-22 30-22s30 8 30 22z", "#c8915a") + _p("M30 66l6 8M44 62l4 10M58 64l2 10", "none", 2.4)
                + "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="#6a3f8a" stroke="{INK}" stroke-width="2.4"/>' for x, y in ((84, 40), (96, 40), (78, 52), (90, 52), (102, 52), (84, 64), (96, 64)))
                + _p("M90 32c0-6 4-10 8-12", "none", 2.4)),
    "bells": _i(_p("M30 76c4-4 6-12 6-24a14 14 0 0 1 28 0c0 12 2 20 6 24z", "#e2b64a") + _p("M56 76c4-4 6-12 6-24a14 14 0 0 1 28 0c0 12 2 20 6 24z", "#e2b64a")
                + '<circle cx="50" cy="82" r="5" fill="#a8802f"/><circle cx="76" cy="82" r="5" fill="#a8802f"/>' + _p("M20 40l-8-4M22 30l-6-8M100 40l8-4M98 30l6-8", "none", 2.6)),
    "host": _i(_p("M40 64c0 16 8 22 20 22s20-6 20-22z", "#e2b64a") + _p("M56 86h8v10h-8zM44 100h32", "#e2b64a", 2.6)
               + '<circle cx="60" cy="38" r="18" fill="#ffffff" stroke="#2a2320" stroke-width="3"/>' + _p("M60 28v20M50 38h20", "none", 2.4)
               + _p("M60 12v-4M34 22l-4-4M86 22l4-4M26 40h-6M94 40h6", "none", 2.6)),
    "pray": _i(_p("M60 16c-4 0-8 4-10 12l-6 30-6 8v18l10 8h12z", "#f2c9a4") + _p("M60 16c4 0 8 4 10 12l6 30 6 8v18l-10 8H60z", "#f2c9a4")
               + _p("M38 84l-6 16h56l-6-16z", "#2f5d9e")),
    "peace": _i(_p("M30 64c10-20 32-26 52-18l14-10-4 16c6 10 2 26-12 32-18 8-40 0-50-20z", "#ffffff") + _p("M48 60c8 10 20 12 30 6", "none", 2.4)
                + '<circle cx="86" cy="50" r="2.6" fill="#2a2320"/>' + _p("M28 64l-12-2 10 8", "#e2b64a", 2.4) + _p("M70 84c4 6 10 10 18 10", "#3f7a4a", 2.4)),
    "communion": _i('<circle cx="60" cy="60" r="26" fill="#ffffff" stroke="#2a2320" stroke-width="3"/>' + _p("M60 46v28M46 60h28", "none", 3)
                    + _p("M60 18v-8M60 110v-8M18 60h-8M110 60h-8M30 30l-6-6M90 30l6-6M30 90l-6 6M90 90l6 6", "none", 3)),
    "sent": _i(_p("M30 96V50c0-16 14-28 30-28s30 12 30 28v46z", "#3f7a4a") + _p("M44 96V56c0-9 7-16 16-16s16 7 16 16v40z", "#f3e2b8")
               + _p("M60 26v-12M54 20h12", "none", 3) + _p("M18 96h84", "none", 3)),
}
