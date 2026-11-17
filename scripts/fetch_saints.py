#!/usr/bin/env python3
"""Builds site/data/saints-directory.json from Wikidata (CC0).

Lists people Wikidata records as Catholic Saints, Blesseds, Venerables and
Servants of God, keeping each person's highest status. Run weekly by
.github/workflows/saints.yml so new decrees show up once Wikidata's
volunteers record them.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "site" / "data" / "saints-directory.json"
ENDPOINT = "https://query.wikidata.org/sparql"
UA = "CatholicDoorwayBot/1.0 (https://catholicdoorway.com; weekly saints list)"

# Wikidata canonization-status values -> our rank (4 Saint, 3 Blessed, 2 Venerable, 1 Servant of God)
STATUS = {
    "Q3464126": 4,   # Catholic saint
    "Q123110154": 4, # canonized saint
    "Q18344276": 4,  # pre-congregation saint
    "Q43115": 4,     # saint (generic: needs a Catholic check)
    "Q2369287": 3,   # blessed
    "Q51619": 2,     # Venerable
    "Q12774503": 2,  # "The Venerable" (generic: needs a Catholic check)
    "Q869974": 1,    # Servant of God
}
GENERIC = {"Q43115", "Q12774503"}
CATHOLIC = {"Q9592", "Q1841", "Q29296"}  # Catholic Church, Catholicism, Latin Church
# Eastern Catholic churches are matched by label below.
SCHISM_YEAR = 1054

QUERY = """
SELECT ?p ?en ?es ?desc ?when ?born ?died
  (GROUP_CONCAT(DISTINCT ?ctryLabel; separator="|") AS ?ctry)
  (GROUP_CONCAT(DISTINCT ?patLabel; separator="|") AS ?pat)
  (GROUP_CONCAT(DISTINCT ?rel; separator="|") AS ?rels)
  (GROUP_CONCAT(DISTINCT ?relLabel; separator="|") AS ?relLabels)
  (SAMPLE(?feastLabel) AS ?feast) (SAMPLE(?wp) AS ?wiki)
WHERE {
  ?p p:P411 ?s . ?s ps:P411 wd:%s . ?p wdt:P31 wd:Q5 .
  OPTIONAL { ?s pq:P585 ?when }
  OPTIONAL { ?p rdfs:label ?en FILTER(lang(?en) = "en") }
  OPTIONAL { ?p rdfs:label ?es FILTER(lang(?es) = "es") }
  OPTIONAL { ?p schema:description ?desc FILTER(lang(?desc) = "en") }
  OPTIONAL { ?p wdt:P569 ?born } OPTIONAL { ?p wdt:P570 ?died }
  OPTIONAL { ?p wdt:P27 ?c . ?c rdfs:label ?ctryLabel FILTER(lang(?ctryLabel) = "en") }
  OPTIONAL { ?p wdt:P417 ?pa . ?pa rdfs:label ?patLabel FILTER(lang(?patLabel) = "en") }
  OPTIONAL { ?p wdt:P140 ?rel . OPTIONAL { ?rel rdfs:label ?relLabel FILTER(lang(?relLabel) = "en") } }
  OPTIONAL { ?p wdt:P841 ?f . ?f rdfs:label ?feastLabel FILTER(lang(?feastLabel) = "en") }
  OPTIONAL { ?wp schema:about ?p ; schema:isPartOf <https://en.wikipedia.org/> }
}
GROUP BY ?p ?en ?es ?desc ?when ?born ?died
"""


def sparql(q, tries=4):
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": q, "format": "json"})
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)["results"]["bindings"]
        except Exception as e:  # noqa: BLE001
            print(f"  retry {i + 1}: {e}", file=sys.stderr)
            time.sleep(20 * (i + 1))
    raise SystemExit("Wikidata query kept failing; keeping old data.")


def year(v):
    m = re.match(r"^(-?\d+)-", v or "")
    if not m:
        return None
    y = int(m.group(1))
    return y if -100 < y < 2100 else None


def val(b, k):
    return b[k]["value"] if k in b else ""


def main():
    people = {}
    for qid, rank in STATUS.items():
        rows = sparql(QUERY % qid)
        print(f"{qid}: {len(rows)} rows")
        for b in rows:
            pid = val(b, "p").rsplit("/", 1)[-1]
            name = val(b, "en") or val(b, "es")
            if not name or re.match(r"^Q\d+$", name):
                continue
            p = people.setdefault(pid, {"rank": 0, "when": None, "generic_only": True, "rels": set(), "relLabels": set()})
            p.update(name=name, es=val(b, "es"), desc=val(b, "desc"), born=year(val(b, "born")) or p.get("born"),
                     died=year(val(b, "died")) or p.get("died"), ctry=val(b, "ctry") or p.get("ctry", ""),
                     pat=val(b, "pat") or p.get("pat", ""), feast=val(b, "feast") or p.get("feast", ""),
                     wiki=val(b, "wiki") or p.get("wiki", ""))
            p["rels"].update(x.rsplit("/", 1)[-1] for x in val(b, "rels").split("|") if x)
            p["relLabels"].update(x for x in val(b, "relLabels").split("|") if x)
            if qid not in GENERIC:
                p["generic_only"] = False
            w = year(val(b, "when"))
            if rank > p["rank"] or (rank == p["rank"] and w and not p["when"]):
                p["rank"], p["when"] = rank, w
        time.sleep(3)

    def catholic_religion(p):
        return bool(p["rels"] & CATHOLIC) or any("Catholic" in r for r in p["relLabels"])

    out, dropped = [], {"other religion": 0, "uncertain": 0}
    for pid, p in people.items():
        cath = catholic_religion(p)
        if p["rels"] and not cath:
            dropped["other religion"] += 1
            continue
        if p["generic_only"] and not cath:
            # A plain "saint" with no religion recorded: keep only the shared saints from before 1054.
            d = p.get("died") or p.get("born")
            if d is None or d >= SCHISM_YEAR:
                dropped["uncertain"] += 1
                continue
        wiki = p["wiki"].rsplit("/wiki/", 1)[-1] if p["wiki"] else ""
        out.append([pid, p["name"], p["es"] if p["es"] != p["name"] else "", p["desc"], p["rank"], p["when"] or 0,
                    p.get("born") or 0, p.get("died") or 0, p["ctry"], p["pat"], p["feast"], urllib.parse.unquote(wiki)])

    out.sort(key=lambda r: r[1].lower())
    counts = {k: sum(1 for r in out if r[4] == v) for k, v in (("saints", 4), ("blessed", 3), ("venerable", 2), ("servants", 1))}
    print(f"Kept {len(out)} people {counts}; dropped {dropped}")
    if len(out) < 3000:
        raise SystemExit("Too few people; keeping old data.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "counts": counts,
            "license": "Data from Wikidata (CC0).",
            "fields": ["qid", "name", "name_es", "desc", "status", "status_year", "born", "died", "countries", "patron_of", "feast", "enwiki"],
            "people": out}
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
