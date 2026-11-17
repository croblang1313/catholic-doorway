#!/usr/bin/env python3
"""Download Catholic churches in the U.S. from OpenStreetMap (Overpass API)
and save them as small static JSON files the map can load directly.

Output: site/data/churches/<lat>_<lon>.json, one file per 1x1 degree cell,
plus site/data/churches/index.json listing the cells and the update date.

Each church is a compact list:
  [lat, lon, name, address, phone, website, service_times, osm_type, osm_id]

Run by .github/workflows/churches.yml every week. Data (c) OpenStreetMap
contributors, ODbL.
"""
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "data" / "churches"
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
DENOMS = ("^(catholic|roman_catholic|greek_catholic|ukrainian_greek_catholic|byzantine_catholic|"
          "ruthenian_catholic|maronite|melkite|chaldean_catholic|armenian_catholic|syro-malabar|"
          "syro_malabar|syro-malankara|syriac_catholic|coptic_catholic|ethiopian_catholic)$")
REGIONS = ("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH "
           "NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR GU VI").split()
UA = "CatholicDoorway church list builder (https://catholicdoorway.com/about)"


def query(region):
    q = (f'[out:json][timeout:180];area["ISO3166-2"="US-{region}"]->.a;'
         f'nwr["amenity"="place_of_worship"]["religion"="christian"]["denomination"~"{DENOMS}"](area.a);'
         'out center tags;')
    data = urllib.parse.urlencode({"data": q}).encode()
    last = None
    for attempt in range(6):
        url = ENDPOINTS[attempt % len(ENDPOINTS)]
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=240) as r:
                return json.load(r)["elements"]
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"  {region}: {url} failed ({e}); retrying", file=sys.stderr)
            time.sleep(15 * (attempt + 1))
    raise RuntimeError(f"{region}: all attempts failed: {last}")


def address(t):
    line1 = " ".join(x for x in [t.get("addr:housenumber"), t.get("addr:street")] if x)
    st = " ".join(x for x in [t.get("addr:state"), t.get("addr:postcode")] if x)
    line2 = ", ".join(x for x in [t.get("addr:city"), st] if x)
    return ", ".join(x for x in [line1, line2] if x)


def compact(el):
    lat = el.get("lat", (el.get("center") or {}).get("lat"))
    lon = el.get("lon", (el.get("center") or {}).get("lon"))
    if lat is None or lon is None:
        return None
    t = el.get("tags", {})
    web = t.get("website") or t.get("contact:website") or t.get("url") or ""
    phone = (t.get("phone") or t.get("contact:phone") or "").split(";")[0].strip()
    return [round(lat, 5), round(lon, 5), t.get("name") or t.get("name:en") or "",
            address(t), phone, web, t.get("service_times", ""), el["type"][0], el["id"]]


def main():
    cells, seen, failed = {}, set(), []
    for region in REGIONS:
        try:
            elements = query(region)
        except RuntimeError as e:
            print(e, file=sys.stderr)
            failed.append(region)
            continue
        n = 0
        for el in elements:
            key = (el["type"], el["id"])
            if key in seen:
                continue
            seen.add(key)
            c = compact(el)
            if not c:
                continue
            cell = f"{math.floor(c[0])}_{math.floor(c[1])}"
            cells.setdefault(cell, []).append(c)
            n += 1
        print(f"{region}: {n} churches")
        time.sleep(5)  # be polite to the shared Overpass servers

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
