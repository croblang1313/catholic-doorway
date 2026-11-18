#!/usr/bin/env python3
"""Builds src/data/dioceses.json: every current U.S. Catholic diocese, archdiocese and eparchy
from Wikidata (CC0), with its bishop, cathedral, website and the holy men and women of its state.
Run weekly by .github/workflows/dioceses.yml, which then rebuilds the site.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "src" / "data" / "dioceses.json"
UA = "CatholicDoorwayBot/1.0 (https://catholicdoorway.com; weekly diocese list)"

CLASSES = "wd:Q3146899 wd:Q105390172 wd:Q373074 wd:Q105389481 wd:Q20725872 wd:Q2665272 wd:Q108822885 wd:Q1531518 wd:Q141603674 wd:Q105406193"

DIOCESES = """
SELECT ?d ?name ?hqLabel ?state ?stateLabel ?state2 ?state2Label ?web ?bishopLabel ?since ?catLabel ?coord ?members ?ch ?gc ?founded
  (GROUP_CONCAT(DISTINCT ?clsLabel; separator="|") AS ?types) WHERE {
  VALUES ?cls { %s }
  ?d wdt:P31 ?cls ; wdt:P17 wd:Q30 . FILTER NOT EXISTS { ?d wdt:P576 [] }
  ?cls rdfs:label ?clsLabel FILTER(lang(?clsLabel) = "en")
  ?d rdfs:label ?name FILTER(lang(?name) = "en")
  OPTIONAL { ?d wdt:P159 ?hq . ?hq rdfs:label ?hqLabel FILTER(lang(?hqLabel) = "en")
             OPTIONAL { ?hq wdt:P131* ?state . ?state wdt:P31 wd:Q35657 . ?state rdfs:label ?stateLabel FILTER(lang(?stateLabel) = "en") } }
  OPTIONAL { ?d wdt:P131 ?loc . ?loc wdt:P131* ?state2 . ?state2 wdt:P31 wd:Q35657 . ?state2 rdfs:label ?state2Label FILTER(lang(?state2Label) = "en") }
  OPTIONAL { ?d wdt:P856 ?web }
  OPTIONAL { ?d p:P488 ?bs . ?bs ps:P488 ?bishop . FILTER NOT EXISTS { ?bs pq:P582 [] }
             ?bishop rdfs:label ?bishopLabel FILTER(lang(?bishopLabel) = "en") OPTIONAL { ?bs pq:P580 ?since } }
  OPTIONAL { ?d wdt:P1885 ?cat . ?cat rdfs:label ?catLabel FILTER(lang(?catLabel) = "en") OPTIONAL { ?cat wdt:P625 ?coord } }
  OPTIONAL { ?d wdt:P2124 ?members }
  OPTIONAL { ?d wdt:P1866 ?ch }
  OPTIONAL { ?d wdt:P8389 ?gc }
  OPTIONAL { ?d wdt:P571 ?founded }
}
GROUP BY ?d ?name ?hqLabel ?state ?stateLabel ?state2 ?state2Label ?web ?bishopLabel ?since ?catLabel ?coord ?members ?ch ?gc ?founded
""" % CLASSES

# Catholic holy people born or died in a U.S. state.
STATUS_RANK = {"Q3464126": 4, "Q123110154": 4, "Q18344276": 4, "Q43115": 4, "Q2369287": 3, "Q51619": 2, "Q12774503": 2, "Q869974": 1}
HOLY = """
SELECT ?p ?pLabel ?st ?stateLabel ?born ?died WHERE {
  VALUES ?st { %s }
  ?p wdt:P411 ?st ; wdt:P31 wd:Q5 .
  { ?p wdt:P19 ?pl } UNION { ?p wdt:P20 ?pl }
  ?pl wdt:P131* ?state . ?state wdt:P31 wd:Q35657 .
  OPTIONAL { ?p wdt:P569 ?born } OPTIONAL { ?p wdt:P570 ?died }
  FILTER NOT EXISTS { ?p wdt:P140 ?r . FILTER(?r IN (wd:Q35032, wd:Q60995, wd:Q178169, wd:Q23540, wd:Q682443, wd:Q75809)) }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
""" % " ".join("wd:" + k for k in STATUS_RANK)


def sparql(q, tries=4):
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": q, "format": "json"})
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)["results"]["bindings"]
        except Exception as e:  # noqa: BLE001
            print(f"  retry {i + 1}: {e}", file=sys.stderr)
            time.sleep(20 * (i + 1))
    raise SystemExit("Wikidata query kept failing; keeping old data.")


def v(b, k):
    return b[k]["value"] if k in b else ""


def slugify(name):
    s = name.lower()
    s = re.sub(r"^(roman catholic |catholic )", "", s)
    s = s.replace("–", "-").replace("’", "").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def year(x):
    m = re.match(r"^(-?\d+)", x or "")
    return int(m.group(1)) if m else 0


def main():
    rows = sparql(DIOCESES)
    print(f"{len(rows)} diocese rows")
    out = {}
    for b in rows:
        qid = v(b, "d").rsplit("/", 1)[-1]
        d = out.setdefault(qid, {"qid": qid, "name": v(b, "name"), "types": set(), "states": set()})
        d["types"].update(t for t in v(b, "types").split("|") if t)
        for k in ("stateLabel", "state2Label"):
            if v(b, k):
                d["states"].add(v(b, k))
        for key, src in (("city", "hqLabel"), ("website", "web"), ("cathedral", "catLabel"), ("ch", "ch"), ("gc", "gc")):
            if v(b, src) and not d.get(key):
                d[key] = v(b, src)
        if v(b, "bishopLabel"):
            since = v(b, "since")[:10]
            # Several open-ended statements: prefer the most recent start date.
            if not d.get("bishop") or since > d.get("bishop_since", ""):
                d["bishop"], d["bishop_since"] = v(b, "bishopLabel"), since
        m = re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", v(b, "coord"))
        if m and not d.get("lat"):
            d["lon"], d["lat"] = round(float(m.group(1)), 4), round(float(m.group(2)), 4)
        if v(b, "members"):
            d["members"] = max(d.get("members", 0), int(float(v(b, "members"))))
        if v(b, "founded") and not d.get("founded"):
            d["founded"] = year(v(b, "founded"))

    holy = sparql(HOLY)
    print(f"{len(holy)} holy-people rows")
    by_state = {}
    for b in holy:
        st = v(b, "stateLabel")
        pid = v(b, "p").rsplit("/", 1)[-1]
        rank = STATUS_RANK.get(v(b, "st").rsplit("/", 1)[-1], 0)
        name = v(b, "pLabel")
        if not st or re.match(r"^Q\d+$", name):
            continue
        cur = by_state.setdefault(st, {}).get(pid)
        if not cur or rank > cur["rank"]:
            by_state[st][pid] = {"qid": pid, "name": name, "rank": rank, "born": year(v(b, "born")), "died": year(v(b, "died"))}

    dioceses = []
    used = set()
    for d in out.values():
        d["types"] = sorted(d["types"])
        d["states"] = sorted(d["states"])
        if "Washington" in d["name"] and not d["states"]:
            d["states"] = ["District of Columbia"]
        slug = slugify(d["name"])
        while slug in used:
            slug += "-" + d["qid"].lower()
        used.add(slug)
        d["slug"] = slug
        dioceses.append(d)
    dioceses.sort(key=lambda d: (d["states"][0] if d["states"] else "~", d["name"]))
    if len(dioceses) < 150:
        raise SystemExit(f"Only {len(dioceses)} dioceses; keeping old data.")
    holy_out = {st: sorted(p.values(), key=lambda p: (-p["rank"], p["name"])) for st, p in by_state.items()}
    OUT.write_text(json.dumps({"updated": time.strftime("%Y-%m-%d"), "source": "Wikidata (CC0)",
                               "dioceses": dioceses, "holy_by_state": holy_out}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {len(dioceses)} dioceses; holy people in {len(holy_out)} states; "
          f"{sum(1 for d in dioceses if d.get('bishop'))} with a bishop, {sum(1 for d in dioceses if d.get('website'))} with a website, "
          f"{sum(1 for d in dioceses if not d['states'])} without a state")


if __name__ == "__main__":
    main()
