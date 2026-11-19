"""The interactive Advent calendar: {{ADVENT_CALENDAR}} on each Advent page.

A church (advent_art.church_svg) with one numbered door or window per day of this
Advent, first Sunday to Christmas Eve. Each door is a link to that day's card, so
without JavaScript the doors jump down a plain list of days; advent.js turns them
into doors that swing open, keeps future days shut and remembers opened doors.

Content: src/data/advent_calendar_<lang>.json, keyed by "MM-DD" for weekdays and
saints' days, plus four Sunday entries. On a Sunday the Sunday entry leads and a
saint's day that falls on it shows underneath as "Also today".
"""
import datetime as dt
import html
import json
from pathlib import Path

import advent_art
import seasons

e = html.escape
DATA = Path(__file__).parent / "data"
WD_SHORT = {
    "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "es": ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"],
    "pt": ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"],
    "tl": ["Lun", "Mar", "Miy", "Huw", "Biy", "Sab", "Lin"],
}


def _load(lang):
    return json.loads((DATA / f"advent_calendar_{lang}.json").read_text(encoding="utf-8"))


def _usccb(ref):
    import features
    return features._usccb(ref)


def plan(y):
    """Every day of the Advent that begins in year y: (date, primary, also) where each is
    ("sunday", week) or ("day", "MM-DD") or None."""
    s = seasons.season_dates(y)
    eve = s["xmas"] - dt.timedelta(days=1)
    days, d = [], s["adv1"]
    while d <= eve:
        key = d.strftime("%m-%d")
        week = sum(1 for a in s["adv"] if a <= d)
        if d == eve:
            prim, also = ("day", key), (("sunday", week) if d.weekday() == 6 else None)
        elif d.weekday() == 6:
            prim, also = ("sunday", week), ("day", key)
        elif s["imm_moved"] and key == "12-09":
            prim, also = ("day", "12-08"), ("day", "12-09")
        else:
            prim, also = ("day", key), None
        days.append(dict(date=d, week=5 if d == eve else week, prim=prim, also=also))
        d += dt.timedelta(days=1)
    return days, s


def _entry(c, ref):
    kind, k = ref
    return c["sundays"][k - 1] if kind == "sunday" else c["days"][k]


def calendar_html(lang, y=None):
    y = seasons.current_year() if y is None else y
    c, en = _load(lang), _load("en")
    ui = c["ui"]
    days, s = plan(y)
    n = len(days)
    iso = [x["date"].isoformat() for x in days]
    slots, spare = advent_art.assign(iso, iso[0], s["adv"][2].isoformat(), iso[-1])
    title = ui["art"].replace("{n}", str(n))
    hl = "" if lang == "en" else ' hreflang="en"'

    doors, cards = [], []
    for i, x in enumerate(days, 1):
        d, day_iso = x["date"], x["date"].isoformat()
        long = seasons.fmt(d, lang)
        sl = advent_art.BY_ID[slots[day_iso]]
        pos = (f'left:{sl["x"] / advent_art.W * 100:.3f}%;top:{sl["y"] / advent_art.H * 100:.3f}%;'
               f'width:{sl["w"] / advent_art.W * 100:.3f}%;height:{sl["h"] / advent_art.H * 100:.3f}%;'
               f'--ry:{advent_art.arch_ry(sl):.1f}%')
        mon = f'<small>{e(ui["months"][0])}</small>' if d.month == 11 else ""
        cls = f'ac-door ac-{sl["shape"]} ac-k-{sl["kind"]}' + (" ac-rose" if sl["id"] == "R" else "") + (" ac-great" if sl["id"] == "D" else "") + (" ac-small" if sl["h"] < 70 else "")
        doors.append(
            f'<a class="{cls}" href="#advent-{day_iso}" data-day="{day_iso}" data-date="{e(long)}" style="{pos}" '
            f'aria-label="{e(ui["open"].replace("{d}", long))}">'
            f'<span class="ac-in"><span class="ac-wd">{e(WD_SHORT[lang][d.weekday()])}</span>'
            f'<span class="ac-dd">{d.day}</span><span class="ac-mo">{e(ui["months"][0 if d.month == 11 else 1])}</span></span>'
            f'<span class="ac-leaf ac-l"></span><span class="ac-leaf ac-r"></span>'
            f'<span class="ac-num">{mon}{d.day}</span></a>')

        p = _entry(c, x["prim"])
        pe = _entry(en, x["prim"])
        ref = p["ref"]
        link = _usccb(pe.get("link", pe["ref"]))
        if lang == "en":
            scripture = (f'<blockquote class="ac-scripture"><p>{e(p["q"])}</p><footer><a href="{link}" target="_blank" '
                         f'rel="noopener" title="{e(ui["read"])}">{e(ref)}</a></footer></blockquote>')
        else:
            scripture = f'<p class="ac-read">{e(ui["read"])}: <a href="{link}" target="_blank" rel="noopener"{hl}>{e(ref)}</a></p>'
        act = p.get("a_moved") if (s["imm_moved"] and x["prim"] == ("day", "12-08")) else p["a"]
        also = ""
        if x["also"]:
            a, ae = _entry(c, x["also"]), _entry(en, x["also"])
            if x["also"][0] == "sunday" or ae.get("feast"):
                note = a.get("a_moved") if (s["imm_moved"] and x["also"] == ("day", "12-08")) else ""
                also = (f'<div class="ac-also"><p class="label">{e(ui["also"])}</p><h4>{e(a["t"])}</h4>'
                        f'<p>{e(a["r"])}</p>{f"<p>{e(note)}</p>" if note else ""}</div>')
        wreath = advent_art.wreath_svg(x["week"], ui["wreath"][x["week"]])
        kicker = f'{e(long)} &middot; {e(ui["day"].replace("{n}", str(i)).replace("{N}", str(n)))}'
        cards.append(
            f'<article class="ac-day" id="advent-{day_iso}" data-day="{day_iso}">'
            f'<div class="ac-day-head"><div><p class="ac-kicker">{kicker}</p><h3>{e(p["t"])}</h3></div>{wreath}</div>'
            f'{scripture}<p class="ac-reflect">{e(p["r"])}</p>'
            f'<p class="ac-do"><strong>{e(ui["todo"])}:</strong> {e(act)}</p>{also}</article>')

    msgs = {k: ui[k] for k in ("wait", "before", "after", "progress", "opened", "locked", "open")}
    first_long = seasons.fmt(days[0]["date"], lang)
    return f'''<div class="ac" id="advent-cal" data-start="{iso[0]}" data-end="{iso[-1]}" data-year="{y}" data-first="{e(first_long)}" data-msgs="{e(json.dumps(msgs, ensure_ascii=False))}">
  <div class="ac-stage">
    <div class="ac-church">{advent_art.church_svg(title, used=set(slots.values()))}
{chr(10).join(doors)}
    </div>
    <div class="ac-side">
      <p class="ac-status" id="ac-status" aria-live="polite"></p>
      <p class="ac-toast" id="ac-toast" role="status" hidden></p>
      <button class="btn" type="button" id="ac-today" hidden>{e(ui["today"])}</button>
      <p class="ac-progress" id="ac-progress"></p>
      <p class="small muted ac-hint">{e(ui["hint"])}</p>
      <button class="btn small secondary" type="button" id="ac-reset" hidden>{e(ui["reset"])}</button>
    </div>
  </div>
  <dialog class="ac-dialog" id="ac-dialog" aria-labelledby="ac-dtitle">
    <div class="ac-dbody" id="ac-dbody"></div>
    <div class="ac-dnav">
      <button class="btn secondary small" type="button" id="ac-prev">{ui["prev"]}</button>
      <button class="btn small" type="button" id="ac-close">{e(ui["close"])}</button>
      <button class="btn secondary small" type="button" id="ac-next">{ui["next"]}</button>
    </div>
  </dialog>
  <div class="ac-days" id="ac-days">
    <h3 class="ac-list-h">{e(ui["list"])}</h3>
{chr(10).join(cards)}
  </div>
</div>'''


def head(lang):
    """Heading and intro for the calendar section."""
    ui = _load(lang)["ui"]
    return f'<h2 style="margin-top:0">{e(ui["h"])}</h2><p class="ac-intro">{e(ui["intro"])}</p>'


def render(body, lang):
    if "{{ADVENT_CALENDAR}}" in body:
        body = body.replace("{{ADVENT_CALENDAR}}", head(lang) + calendar_html(lang))
    return body
