#!/usr/bin/env python3
"""Build the U.S. Catholic church list from OpenStreetMap extracts and save it
as small static JSON files the map can load directly.

The public Overpass servers proved too busy to answer state-sized queries, so
this downloads Geofabrik's per-state extracts instead (one at a time, deleting
each after use), keeps only places of worship with `osmium tags-filter`, and
reads the result with pyosmium.

Output: site/data/churches/<lat>_<lon>.json, one file per 1x1 degree cell,
plus site/data/churches/index.json listing the cells and the update date.

Each church is a compact list:
  [lat, lon, name, address, phone, website, service_times, osm_type, osm_id]

Needs: the `osmium` command (apt: osmium-tool) and `pip install osmium`.
Run by .github/workflows/churches.yml every week. Data (c) OpenStreetMap
contributors, ODbL.
"""
import json
import math
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import osmium

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "data" / "churches"
INDEX_URL = "https://download.geofabrik.de/index-v1-nogeom.json"
UA = "CatholicDoorway church list builder (https://catholicdoorway.com/about)"
DENOMS = re.compile(
    r"^(catholic|roman_catholic|greek_catholic|ukrainian_greek_catholic|byzantine_catholic|"
    r"ruthenian_catholic|maronite|melkite|chaldean_catholic|armenian_catholic|syro-malabar|"
    r"syro_malabar|syro-malankara|syriac_catholic|coptic_catholic|ethiopian_catholic)$")


def fetch(url, dest=None):
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=600) as r:
                if dest is None:
                    return r.read()
                with open(dest, "wb") as f:
                    while chunk := r.read(1 << 20):
                        f.write(chunk)
                return dest
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"  {url} failed ({e}); retrying", file=sys.stderr)
            time.sleep(20 * (attempt + 1))
    raise RuntimeError(f"{url}: {last}")


US_PLACES = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut",
    "delaware", "district of columbia", "florida", "georgia", "hawaii", "idaho", "illinois",
    "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland",
    "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana",
    "nebraska", "nevada", "new hampshire", "new jersey", "new mexico", "new york",
    "north carolina", "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania",
    "rhode island", "south carolina", "south dakota", "tennessee", "texas", "utah",
    "vermont", "virginia", "washington", "west virginia", "wisconsin", "wyoming",
    "puerto rico", "guam", "american samoa", "northern mariana islands",
    "united states virgin islands", "us virgin islands",
}


def us_extracts():
    """The Geofabrik extracts for each U.S. state, DC and territory.

    Found by walking the index's parent links down from the United States
    entry and matching place names, so it keeps working when Geofabrik moves
    the states into a new folder layout (as it did in November 2026, which
    broke the old "/north-america/us/<state>" URL match).
    """
    idx = json.loads(fetch(INDEX_URL))
    props = [f["properties"] for f in idx["features"]]
    kids = {}
    for p in props:
        kids.setdefault(p.get("parent"), []).append(p)
    roots = [p for p in props if p["id"] in ("us", "united-states", "united-states-of-america")
             or p.get("name", "").lower() in ("united states", "united states of america")]
    out, queue = {}, [r["id"] for r in roots]
    while queue:
        for p in kids.get(queue.pop(), []):
            queue.append(p["id"])
            name = re.sub(r"\s+", " ", p.get("name", "").lower().replace("-", " ")).strip()
            slug = p["id"].rsplit("/", 1)[-1].replace("-", " ")
            pbf = p.get("urls", {}).get("pbf")
            key = name if name in US_PLACES else slug if slug in US_PLACES else None
            if pbf and key and key not in out:
                out[key] = (p["id"], pbf)
    if len(out) < 50:
        sample = [(p["id"], p.get("parent"), p.get("urls", {}).get("pbf")) for p in props
                  if "us" in (p.get("parent") or "") or "/us" in p.get("urls", {}).get("pbf", "")][:25]
        print("U.S. roots found:", [r["id"] for r in roots], file=sys.stderr)
        print("Sample of U.S.-looking entries:", *sample, sep="\n  ", file=sys.stderr)
        sys.exit(f"Geofabrik index lists only {len(out)} U.S. extracts; keeping old data.")
    print(f"Found {len(out)} U.S. extracts.", flush=True)
    return sorted(out.values())


def is_catholic(t):
    return (t.get("amenity") == "place_of_worship" and t.get("religion") == "christian"
            and DENOMS.match(t.get("denomination", "")))


def address(t):
    line1 = " ".join(x for x in [t.get("addr:housenumber"), t.get("addr:street")] if x)
    st = " ".join(x for x in [t.get("addr:state"), t.get("addr:postcode")] if x)
    line2 = ", ".join(x for x in [t.get("addr:city"), st] if x)
    return ", ".join(x for x in [line1, line2] if x)


def compact(lat, lon, t, kind, oid):
    web = t.get("website") or t.get("contact:website") or t.get("url") or ""
    phone = (t.get("phone") or t.get("contact:phone") or "").split(";")[0].strip()
    email = (t.get("email") or t.get("contact:email") or "").split(";")[0].strip()
    return [round(lat, 5), round(lon, 5), t.get("name") or t.get("name:en") or "",
            address(t), phone, web, t.get("service_times", ""), kind, oid, email]


class Churches(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.found = []

    def node(self, n):
        t = dict(n.tags)
        if is_catholic(t) and n.location.valid():
            self.found.append(compact(n.location.lat, n.location.lon, t, "n", n.id))

    def area(self, a):
        t = dict(a.tags)
        if not is_catholic(t):
            return
        pts = [(nd.lat, nd.lon) for ring in a.outer_rings() for nd in ring if nd.location.valid()]
        if not pts:
            return
        lat = sum(p[0] for p in pts) / len(pts)
        lon = sum(p[1] for p in pts) / len(pts)
        self.found.append(compact(lat, lon, t, "w" if a.from_way() else "r", a.orig_id()))


def churches_in(region, url, tmp):
    """Download one extract, keep its places of worship, return the Catholic ones."""
    work = Path(tmp) / region.replace("/", "_")
    work.mkdir()
    raw, small = work / "region.osm.pbf", work / "pow.osm.pbf"
    fetch(url, raw)
    subprocess.run(["osmium", "tags-filter", "--overwrite", "-o", str(small), str(raw),
                    "nwr/amenity=place_of_worship"], check=True, capture_output=True)
    raw.unlink()
    h = Churches()
    h.apply_file(str(small), locations=True)
    small.unlink()
    return h.found


def main():
    cells, seen, failed = {}, set(), []
    # Geofabrik serves each download slowly, so fetch a few states at once.
    with tempfile.TemporaryDirectory() as tmp, ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(churches_in, region, url, tmp): region for region, url in us_extracts()}
        for job in as_completed(jobs):
            region = jobs[job]
            try:
                found = job.result()
            except Exception as e:  # noqa: BLE001
                print(f"{region}: failed ({e})", file=sys.stderr, flush=True)
                failed.append(region)
                continue
            n = 0
            for c in found:
                key = (c[7], c[8])  # state extracts overlap at borders
                if key in seen:
                    continue
                seen.add(key)
                cells.setdefault(f"{math.floor(c[0])}_{math.floor(c[1])}", []).append(c)
                n += 1
            print(f"{region}: {n} churches", flush=True)

    if len(failed) > 5 or len(seen) < 5000:
        sys.exit(f"Too many failures ({failed}) or too few churches ({len(seen)}); keeping old data.")

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for cell, items in cells.items():
        items.sort(key=lambda c: c[2])
        (OUT / f"{cell}.json").write_text(json.dumps(items, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    index = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "count": len(seen),
             "cells": sorted(cells), "failed_regions": failed,
             "license": "Data (c) OpenStreetMap contributors, ODbL 1.0"}
    (OUT / "index.json").write_text(json.dumps(index, separators=(",", ":")), encoding="utf-8")
    print(f"Saved {len(seen)} churches in {len(cells)} cells. Failed: {failed or 'none'}")


if __name__ == "__main__":
    main()
