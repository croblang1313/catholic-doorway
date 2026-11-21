"""Print the license line of each Piper voice we might use (run in CI)."""
import json, re, urllib.request
BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
voices = json.load(urllib.request.urlopen(BASE + "voices.json"))
for key, v in sorted(voices.items()):
    lang = v["language"]["code"]
    if not re.match(r"(en_US|en_GB|es_|pt_|it_IT|fil|tl)", lang):
        continue
    card = [f for f in v["files"] if f.endswith("MODEL_CARD")]
    lic = "?"
    if card:
        try:
            txt = urllib.request.urlopen(BASE + card[0]).read().decode("utf-8", "replace")
            lic = " / ".join(l.strip() for l in txt.splitlines() if re.search(r"licen|dataset|http", l, re.I))[:400]
        except Exception as e:
            lic = "err %s" % e
    print(f"{key} | speakers={v.get('num_speakers')} | {lic}")
