#!/usr/bin/env python3
"""Runs one Wikidata SPARQL query (from $QUERY) and prints the results as TSV. Used by probe.yml."""
import json, os, urllib.parse, urllib.request
q = os.environ["QUERY"]
url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": q, "format": "json"})
req = urllib.request.Request(url, headers={"User-Agent": "CatholicDoorwayBot/1.0 (https://catholicdoorway.com)"})
d = json.load(urllib.request.urlopen(req, timeout=120))
vs = d["head"]["vars"]
print("\t".join(vs))
for b in d["results"]["bindings"]:
    print("\t".join(b.get(v, {}).get("value", "").replace("http://www.wikidata.org/entity/", "") for v in vs))
print(f"# {len(d['results']['bindings'])} rows")
