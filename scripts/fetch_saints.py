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

STATUS_QUERY = """
SELECT ?p ?when WHERE {
  ?p p:P411 ?s . ?s ps:P411 wd:%s . ?p wdt:P31 wd:Q5 .
  OPTIONAL { ?s pq:P585 ?when }
}
"""

DETAIL_QUERY = """
SELECT ?p ?en ?es ?desc ?born ?died
  (GROUP_CONCAT(DISTINCT ?ctryLabel; separator="|") AS ?ctry)
  (GROUP_CONCAT(DISTINCT ?patLabel; separator="|") AS ?pat)
  (GROUP_CONCAT(DISTINCT ?rel; separator="|") AS ?rels)
  (GROUP_CONCAT(DISTINCT ?relLabel; separator="|") AS ?relLabels)
  (SAMPLE(?feastLabel) AS ?feast) (SAMPLE(?wp) AS ?wiki)
WHERE {
  VALUES ?p { %s }
  OPTIONAL { ?p rdfs:label ?en FILTER(lang(?en) = "en") }
  OPTIONAL { ?p rdfs:label ?es FILTER(lang(?es) = "es") }
  OPTIONAL { ?p schema:description ?desc FILTER(lang(?desc) = "en") }
  OPTIONAL { ?p wdt:P569 ?born } OPTIONAL { ?p wdt:P570 ?died }
  OPTIONAL { ?p wdt:P27 ?c . ?c rdfs:label ?ctryLabel FILTER(lang(?ctryLabel) = "en") }
  OPTIONAL { ?pa wdt:P417 ?p . ?pa rdfs:label ?patLabel FILTER(lang(?patLabel) = "en") }
  OPTIONAL { ?p wdt:P140 ?rel . OPTIONAL { ?rel rdfs:label ?relLabel FILTER(lang(?relLabel) = "en") } }
  OPTIONAL { ?p wdt:P841 ?f . ?f rdfs:label ?feastLabel FILTER(lang(?feastLabel) = "en") }
  OPTIONAL { ?wp schema:about ?p ; schema:isPartOf <https://en.wikipedia.org/> }
}
GROUP BY ?p ?en ?es ?desc ?born ?died
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


COUNTRY_MAP = {
    "Kingdom of Italy": "Italy", "Papal States": "Italy", "Republic of Venice": "Italy", "Republic of Genoa": "Italy",
    "Kingdom of Naples": "Italy", "Kingdom of Sicily": "Italy", "Kingdom of the Two Sicilies": "Italy", "Duchy of Milan": "Italy",
    "Republic of Florence": "Italy", "Grand Duchy of Tuscany": "Italy", "Kingdom of Sardinia": "Italy", "Duchy of Savoy": "Italy",
    "Kingdom of France": "France", "French First Republic": "France", "First French Empire": "France", "French Third Republic": "France",
    "Francia": "France", "Kingdom of the Franks": "France", "West Francia": "France",
    "Crown of Castile": "Spain", "Kingdom of Castile": "Spain", "Crown of Aragon": "Spain", "Kingdom of Aragon": "Spain",
    "Kingdom of León": "Spain", "Kingdom of Navarre": "Spain", "Spanish Empire": "Spain", "Second Spanish Republic": "Spain",
    "Francoist Spain": "Spain", "Kingdom of Spain": "Spain",
    "Kingdom of Portugal": "Portugal", "Second Polish Republic": "Poland", "Polish–Lithuanian Commonwealth": "Poland",
    "Kingdom of Poland": "Poland", "Congress Poland": "Poland", "Polish People's Republic": "Poland",
    "Kingdom of England": "England", "Kingdom of Scotland": "Scotland", "Kingdom of Ireland": "Ireland",
    "United Kingdom of Great Britain and Ireland": "United Kingdom", "Kingdom of Great Britain": "United Kingdom",
    "Holy Roman Empire": "Germany", "German Empire": "Germany", "Nazi Germany": "Germany", "Weimar Republic": "Germany",
    "Kingdom of Prussia": "Germany", "Kingdom of Bavaria": "Germany", "West Germany": "Germany", "East Francia": "Germany",
    "Austria–Hungary": "Austria-Hungary", "Austrian Empire": "Austria", "Archduchy of Austria": "Austria",
    "Kingdom of Hungary": "Hungary", "Kingdom of Yugoslavia": "Yugoslavia", "Kingdom of Bohemia": "Czech lands",
    "Czechoslovakia": "Czech lands", "Czech Republic": "Czech lands", "Ancient Rome": "Roman Empire", "Roman Republic": "Roman Empire",
    "Western Roman Empire": "Roman Empire", "Byzantine Empire": "Byzantine Empire", "Carolingian Empire": "France",
    "New Spain": "Mexico", "Viceroyalty of Peru": "Peru", "Empire of Brazil": "Brazil", "Kingdom of the Netherlands": "Netherlands",
    "Dutch Republic": "Netherlands", "Spanish Netherlands": "Belgium", "Dominion of India": "India", "British Raj": "India",
}


def norm_countries(c):
    seen = []
    for x in c.split("|"):
        x = COUNTRY_MAP.get(x.strip(), x.strip())
        if x and x not in seen:
            seen.append(x)
    return "|".join(seen)


def main():
    people = {}
    for qid, rank in STATUS.items():
        rows = sparql(STATUS_QUERY % qid)
        print(f"{qid}: {len(rows)} people")
        for b in rows:
            pid = val(b, "p").rsplit("/", 1)[-1]
            p = people.setdefault(pid, {"rank": 0, "when": None, "generic_only": True, "rels": set(), "relLabels": set()})
            if qid not in GENERIC:
                p["generic_only"] = False
            w = year(val(b, "when"))
            if rank > p["rank"] or (rank == p["rank"] and w and not p["when"]):
                p["rank"], p["when"] = rank, w
        time.sleep(2)

    ids = list(people)
    for i in range(0, len(ids), 250):
        chunk = ids[i:i + 250]
        rows = sparql(DETAIL_QUERY % " ".join("wd:" + x for x in chunk))
        for b in rows:
            pid = val(b, "p").rsplit("/", 1)[-1]
            p = people[pid]
            p.update(name=val(b, "en") or val(b, "es") or p.get("name", ""), es=val(b, "es"), desc=val(b, "desc"),
                     born=year(val(b, "born")) or p.get("born"), died=year(val(b, "died")) or p.get("died"),
                     ctry=val(b, "ctry"), pat=val(b, "pat"), feast=val(b, "feast"), wiki=val(b, "wiki"))
            p["rels"].update(x.rsplit("/", 1)[-1] for x in val(b, "rels").split("|") if x)
            p["relLabels"].update(x for x in val(b, "relLabels").split("|") if x)
        print(f"details {min(i + 250, len(ids))}/{len(ids)}")
        time.sleep(1)
    people = {k: v for k, v in people.items() if v.get("name") and not re.match(r"^Q\d+$", v["name"])}

    def catholic_religion(p):
        return bool(p["rels"] & CATHOLIC) or any("Catholic" in r for r in p["relLabels"])

    CATH_HINT = re.compile(r"catholic|\bpope\b|jesuit|francisc|dominican|benedictin|carmelit|augustinian|capuchin|cistercian|"
                           r"salesian|ursuline|redemptorist|passionist|vincentian|poor clare|beatified|canonized|blessed", re.I)
    OTHER_HINT = re.compile(r"orthodox|anglican|lutheran|coptic|armenian apostolic|protestant|methodist|baptist", re.I)
    CATH_LANDS = {"Spain", "France", "Italy", "Poland", "Portugal", "Ireland", "Mexico", "Brazil", "Philippines", "Belgium",
                  "Austria", "Argentina", "Colombia", "Peru", "Chile", "Croatia", "Slovakia", "Lithuania", "Malta", "Hungary",
                  "Canada", "United States", "Germany", "Netherlands", "Switzerland", "Czech Republic", "Slovenia", "Vietnam",
                  "Ecuador", "Venezuela", "Bolivia", "Paraguay", "Uruguay", "Guatemala", "Cuba", "Luxembourg", "Monaco"}

    out, dropped = [], {"other religion": 0, "uncertain": 0}
    for pid, p in people.items():
        p["ctry"] = norm_countries(p.get("ctry", ""))
        cath = catholic_religion(p)
        desc = p.get("desc", "")
        if (p["rels"] and not cath) or (not cath and OTHER_HINT.search(desc) and not CATH_HINT.search(desc)):
            dropped["other religion"] += 1
            continue
        if p["generic_only"] and not cath:
            # A plain "saint" with no religion recorded: keep shared saints from before 1054,
            # and later ones only with a clear Catholic sign.
            d = p.get("died") or p.get("born")
            lands = set(p["ctry"].split("|")) if p["ctry"] else set()
            if (d is None or d >= SCHISM_YEAR) and not (CATH_HINT.search(desc) or lands & CATH_LANDS or p["when"]):
                dropped["uncertain"] += 1
                continue
        wiki = p["wiki"].rsplit("/wiki/", 1)[-1] if p["wiki"] else ""
        out.append([pid, p["name"], p["es"] if p["es"] != p["name"] else "", p["desc"], p["rank"], p["when"] or 0,
                    p.get("born") or 0, p.get("died") or 0, p["ctry"], p["pat"], p["feast"], urllib.parse.unquote(wiki)])

    for pid, p in people.items():
        if re.search(r"Acutis|Seton|Tolton", p.get("name", "")):
            print("DEBUG", pid, p["name"], p["rank"], p["generic_only"], sorted(p["rels"]), sorted(p["relLabels"]), p.get("died"), p.get("ctry"))
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
